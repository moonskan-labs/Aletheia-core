"""Batch runner, source check and report: offline, with no labels in any request."""

import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from research_fixtures import Providers
from test_providers import settings as provider_settings

from aletheia.config import ConfigurationError
from aletheia.evaluation import BatchClaim, load_claims_csv, score_claim
from aletheia.source_check import (
    check_claim,
    check_units,
    fault_stage,
    report_csv,
    report_rows,
    report_summary,
)

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location(
    "batch_runner", ROOT / "scripts" / "evaluate_research.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
CLAIMS = ROOT / "evals" / "claims" / "claims-20261115.csv"


def claim(identifier="b-01", text="The Archive opened in 2000.", **changes):
    return BatchClaim.model_validate(
        {
            "id": identifier,
            "split": "tuning",
            "claim": text,
            "case_type": "direct_fact",
            "expected_outcome": "decided",
            "expected_verdict": "true",
            "unable_reason": None,
            "sources": [{"url": "https://example.org/secret-label", "shows": "Secret reference."}],
            "note": "Secret evaluator note.",
            **changes,
        }
    )


@pytest.fixture
def batch(tmp_path, monkeypatch):
    providers = Providers()
    monkeypatch.setattr(
        runner.ProviderSettings, "from_environment", lambda **kw: provider_settings()
    )

    class Transport(runner.MeteredTransport):
        def __init__(self, provider, attempts):
            self.provider, self.attempts = provider, attempts
            self.inner = httpx.MockTransport(providers.handle)

    monkeypatch.setattr(runner, "MeteredTransport", Transport)
    args = SimpleNamespace(
        dotenv=None, model=None, output=tmp_path / "run", split=None, parallel=2, resume=False
    )
    return args, providers


def test_claims_file_loads_with_splits_and_requests_carry_only_the_claim():
    claims = load_claims_csv(CLAIMS)
    assert len(claims) == 120
    assert len(load_claims_csv(CLAIMS, split="tuning")) == 80
    assert len(load_claims_csv(CLAIMS, split="heldout")) == 40
    assert all(c.request() == {"claim": c.claim} for c in claims)
    with pytest.raises(ValueError):
        load_claims_csv(CLAIMS, split="tuning", ids=["nope"])


async def test_batch_runs_in_parallel_saves_one_file_per_claim_and_leaks_no_labels(batch):
    args, providers = batch
    claims = [claim(), claim("b-02", "The Archive opened in 2000 in Paris.")]
    assert await runner.run_batch(args, claims)
    for item in claims:
        saved = json.loads((args.output / "claims" / f"{item.id}.json").read_text())
        assert saved["investigation"]["status"] in {"completed", "partial"}
        assert saved["events"] and "evidence" in saved
        assert json.loads((args.output / "snapshots" / f"{item.id}.json").read_text())
    sent = json.dumps(providers.model_inputs) + json.dumps([str(c) for c in providers.calls])
    assert "Secret" not in sent and "secret-label" not in sent
    manifest = json.loads((args.output / "manifest.json").read_text())
    assert manifest["recorded"] == 2 and manifest["not_run"] == 0
    assert "api_key" not in json.dumps(manifest)


async def test_resume_runs_only_unfinished_claims_and_never_reruns_a_finished_one(batch):
    args, providers = batch
    first, second = claim(), claim("b-02", "The Archive opened in 2000 in Paris.")
    assert await runner.run_batch(args, [first])
    before = (args.output / "claims" / "b-01.json").read_text()
    with pytest.raises(FileExistsError):  # no silent reuse without --resume
        await runner.run_batch(args, [first])
    args.resume = True
    with pytest.raises(ConfigurationError):  # a different dataset is a different batch
        await runner.run_batch(args, [first, second])
    manifest = args.output / "manifest.json"
    saved = json.loads(manifest.read_text())
    saved["dataset_sha256"] = runner.dataset_hash([first, second])
    manifest.write_text(json.dumps(saved))
    calls = len(providers.calls)
    assert await runner.run_batch(args, [first, second])
    assert (args.output / "claims" / "b-01.json").read_text() == before
    assert (args.output / "claims" / "b-02.json").exists() and len(providers.calls) > calls
    assert len(json.loads(manifest.read_text())["sessions"]) == 2


@pytest.fixture
async def finished(batch):
    args, _ = batch
    item = claim()
    await runner.run_batch(args, [item])
    artifact = json.loads((args.output / "claims" / "b-01.json").read_text())
    snapshots = json.loads((args.output / "snapshots" / "b-01.json").read_text())
    return item, artifact, snapshots


async def test_source_check_accepts_real_passages_and_rejects_tampering(finished):
    item, artifact, snapshots = finished
    units = check_units(artifact, snapshots)
    assert units and all(u["citations_valid"] for u in units)

    changed = copy.deepcopy(artifact)
    changed["evidence"]["evidence"][0]["excerpts"][0]["text"] += " and was famous"
    assert not all(u["citations_valid"] for u in check_units(changed, snapshots))

    other_page = copy.deepcopy(snapshots)
    other_page[0]["normalized_text"] = other_page[0]["normalized_text"].replace("2000", "1999")
    problems = {c["problem"] for u in check_units(artifact, other_page) for c in u["citations"]}
    assert problems == {"page_hash_or_url_mismatch"}

    assert {c["problem"] for u in check_units(artifact, []) for c in u["citations"]} == {
        "snapshot_missing"
    }


async def test_judge_sees_statement_and_passages_but_no_labels(finished):
    item, artifact, snapshots = finished
    seen = []

    class Judge:
        async def generate(self, *, instructions, input_text, response_type, budget):
            seen.append(input_text)
            fields = response_type.model_fields
            value = {"reason": "ok", **({"verdict": "supported"} if "verdict" in fields else {})}
            if "relation" in fields:
                value["relation"] = "agrees"
            return SimpleNamespace(value=response_type.model_validate(value))

    checked = await check_claim(item, artifact, snapshots, Judge())
    assert all(u["judgement"]["verdict"] == "supported" for u in checked["units"])
    assert checked["labelled_source"] == "absent"
    assert checked["labelled_source_agreement"] is None
    support_calls = [text for text in seen if '"statement"' in text]
    assert support_calls and not any("Secret" in text for text in support_calls)
    assert len(seen) == len(support_calls)
    assert not any("Secret" in text or "secret-label" in text for text in seen)


async def test_report_scores_against_labels_and_keeps_conflict_out_of_the_headline(finished):
    item, artifact, snapshots = finished
    assert score_claim(item, artifact)["match"] is True
    wrong = claim(expected_verdict="false")
    conflict = claim(
        "x-01",
        case_type="conflict",
        expected_outcome="unable_to_decide",
        expected_verdict=None,
        unable_reason="conflicting_evidence",
    )
    assert fault_stage(wrong, score_claim(wrong, artifact), artifact, None) == "passage reading"
    no_run = {"investigation": {"status": "needs_clarification"}}
    assert fault_stage(item, score_claim(item, no_run), no_run, None) == "interpretation"
    check = await check_claim(item, artifact, snapshots)
    bad = copy.deepcopy(check)
    bad["units"][0]["citations_valid"] = False
    assert fault_stage(item, score_claim(item, artifact), artifact, check) is None
    assert fault_stage(item, score_claim(item, artifact), artifact, bad) == "bad citations"

    rows = report_rows(
        [item, conflict], {"b-01": artifact, "x-01": artifact}, {"b-01": check, "x-01": check}
    )
    assert report_csv(rows).splitlines()[0].startswith("id,split,case_type,expected,actual,match")
    summary = report_summary(rows, {"model": "m", "revision": "abc"}, 2)
    assert "(conflict group excluded): 1/1 (100%)" in summary
    assert "(all claims): 1/2 (50%)" in summary
