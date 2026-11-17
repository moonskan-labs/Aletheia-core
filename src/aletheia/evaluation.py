"""Opt-in evaluation support. Expected labels never enter research requests."""

import asyncio
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from typing import Literal

from httpx import AsyncClient
from pydantic import BaseModel, ConfigDict, Field, model_validator

from aletheia.contracts import InvestigationRequest


class EvaluationRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ExpectedCorrection(EvaluationRecord):
    what_is_correct: str = Field(min_length=10)
    what_needs_correction: str = Field(min_length=10)
    corrected_claim: str = Field(min_length=10)


class ExpectedDecision(EvaluationRecord):
    outcome: Literal["decided", "unable_to_decide"]
    verdict: Literal["true", "false", "almost"] | None
    unable_to_decide_reason: Literal["insufficient_evidence", "conflicting_evidence"] | None
    expected_correction: ExpectedCorrection | None

    @model_validator(mode="after")
    def consistent(self):
        decided = self.outcome == "decided"
        if decided != (self.verdict is not None) or decided == (
            self.unable_to_decide_reason is not None
        ):
            raise ValueError("Inconsistent expected decision")
        if (self.verdict == "almost") != (self.expected_correction is not None):
            raise ValueError("Only Almost needs a correction")
        return self


class ExpectedFlag(EvaluationRecord):
    type: Literal["misleading_comparison", "narrow_scope"]
    dimension: Literal[
        "population",
        "timeframe",
        "units",
        "baseline",
        "condition",
        "jurisdiction",
        "definition",
        "evaluation_setup",
        "benchmark_subset",
    ]
    rationale: str = Field(min_length=10)


class KeySource(EvaluationRecord):
    url: str = Field(pattern=r"^https?://")
    shows: str = Field(min_length=10)


class EvaluationCase(EvaluationRecord):
    id: str = Field(pattern=r"^[a-z][a-z0-9-]{1,39}$")
    split: Literal["tuning"]
    claim: str = Field(min_length=10, max_length=500)
    context: dict[str, str] = Field(default_factory=dict)
    case_type: Literal[
        "direct_fact", "comparison", "causal", "interpretive", "conflict", "insufficient"
    ]
    expected: ExpectedDecision
    acceptable_alternatives: list[ExpectedDecision]
    expected_flags: list[ExpectedFlag]
    key_sources: list[KeySource] = Field(min_length=1, max_length=3)
    as_of: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    labelers: list[str]
    status: Literal["proposed", "reconciled", "contested"]
    reviewer_note: str = Field(min_length=1)

    @model_validator(mode="after")
    def valid_case(self):
        import datetime

        datetime.date.fromisoformat(self.as_of)
        InvestigationRequest(claim=self.claim, context=self.context)
        if self.status == "proposed" and self.labelers:
            raise ValueError("AI proposals must not assert human labelers")
        if self.status != "proposed" and len(set(self.labelers)) < 2:
            raise ValueError("Reviewed records need two distinct labelers")
        pairs = [(f.type, f.dimension) for f in self.expected_flags]
        if len(pairs) != len(set(pairs)):
            raise ValueError("Duplicate expected flag")
        decisions = [decision_key(d.model_dump()) for d in self.decisions]
        if len(decisions) != len(set(decisions)):
            raise ValueError("Duplicate expected decision")
        for decision in self.decisions:
            correction = decision.expected_correction
            if (
                correction
                and correction.corrected_claim.strip().casefold() == self.claim.strip().casefold()
            ):
                raise ValueError("Almost must correct the claim")
        return self

    @property
    def decisions(self):
        return [self.expected, *self.acceptable_alternatives]

    def request(self):
        # Deliberate allowlist: no sources, expectations, or reviewer notes enter prompts.
        return {"claim": self.claim, **({"context": self.context} if self.context else {})}


def load_cases(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Evaluation requires a nonempty array")
    cases = [EvaluationCase.model_validate(item) for item in data]
    if len({c.id for c in cases}) != len(cases):
        raise ValueError("Duplicate case IDs")
    requests = [InvestigationRequest.model_validate(c.request()).request_key() for c in cases]
    if len(set(requests)) != len(requests):
        raise ValueError("Duplicate requests would reuse research")
    return cases


def decision_key(decision):
    return tuple(decision.get(k) for k in ("outcome", "verdict", "unable_to_decide_reason"))


def score(case, artifact):
    investigation = artifact.get("investigation") or {}
    result = investigation.get("result") or {}
    completed = investigation.get("status") == "completed" and result.get("outcome") in {
        "decided",
        "unable_to_decide",
    }
    match = bool(result) and any(
        decision_key(result) == decision_key(d.model_dump()) for d in case.decisions
    )
    needs_correction_review = completed and match and result.get("verdict") == "almost"
    # A matching Almost label is not a correct answer until all correction parts are reviewed.
    correct = None if needs_correction_review else completed and match
    actual_flags = {
        (f["type"], f["dimension"])
        for f in result.get("finding", {}).get("qualification_flags", [])
    }
    expected_flags = {(f.type, f.dimension) for f in case.expected_flags}
    return {
        "id": case.id,
        "status": investigation.get("status", "runner_failed"),
        "label_status": case.status,
        "decision_label_match": completed and match,
        "decision_correct": correct,
        "almost_review": "pending_human_review" if needs_correction_review else "not_applicable",
        "citation_review": "pending_human_review" if result else "no_result",
        "flags": {
            kind: {
                "tp": sum(p[0] == kind for p in actual_flags & expected_flags),
                "fp": sum(p[0] == kind for p in actual_flags - expected_flags),
                "fn": sum(p[0] == kind for p in expected_flags - actual_flags),
            }
            for kind in ("misleading_comparison", "narrow_scope")
        },
    }


def summarize(rows, planned):
    def group(selected):
        count = len(selected)
        confirmed = sum(r["decision_correct"] is True for r in selected)
        pending = sum(r["decision_correct"] is None for r in selected)
        flags = {}
        for kind in ("misleading_comparison", "narrow_scope"):
            totals = {k: sum(r["flags"][kind][k] for r in selected) for k in ("tp", "fp", "fn")}
            tp, fp, fn = (totals[k] for k in ("tp", "fp", "fn"))
            flags[kind] = {
                **totals,
                "precision": tp / (tp + fp) if tp + fp else None,
                "recall": tp / (tp + fn) if tp + fn else None,
            }
        return {
            "count": count,
            "correct_by_label_rules": confirmed,
            "pending_correction_review": pending,
            "provisional_accuracy_lower_bound": confirmed / count if count else None,
            "provisional_accuracy_upper_bound": (confirmed + pending) / count if count else None,
            "statuses": dict(Counter(r["status"] for r in selected)),
            "flags": flags,
        }

    return {
        "planned": planned,
        "recorded": len(rows),
        "not_run": planned - len(rows),
        "human_acceptance_complete": False,
        "note": (
            "Provisional label comparison only. Human label/citation review is separate; "
            "failures remain in denominators."
        ),
        "all": group(rows),
        "excluding_contested": group([r for r in rows if r["label_status"] != "contested"]),
    }


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_events(text):
    return [json.loads(line[6:]) for line in text.splitlines() if line.startswith("data: ")]


async def get_json(client, path):
    response = await client.get(path)
    response.raise_for_status()
    return response.json()


async def wait_terminal(client, path):
    async with asyncio.timeout(260):
        while True:
            saved = await get_json(client, path)
            if saved["status"] not in {"queued", "running"}:
                return saved
            await asyncio.sleep(0.25)


async def capture(client: AsyncClient, case, *, call_count, refresh=False):
    started = time.monotonic()
    response = await client.post("/investigations", json=case.request())
    response.raise_for_status()
    if response.json()["reused"]:
        raise RuntimeError("Evaluation submission unexpectedly reused prior research")
    path = response.json()["links"]["self"]
    saved = await wait_terminal(client, path)
    before = call_count()
    evidence = await get_json(client, path + "/evidence")
    comparison = await get_json(client, path + "/comparison")
    stream = await client.get(path + "/events")
    stream.raise_for_status()
    events = parse_events(stream.text)
    cursor = events[len(events) // 2]["sequence"]
    replay = await client.get(path + "/events", headers={"Last-Event-ID": str(cursor)})
    replay.raise_for_status()
    duplicate = await client.post("/investigations", json=case.request())
    duplicate.raise_for_status()
    reads = {
        "same_saved_response": duplicate.json() == saved == await get_json(client, path),
        "zero_provider_calls": call_count() == before,
        "ordered_events": [e["sequence"] for e in events] == list(range(1, len(events) + 1)),
        "reconnect_replay": parse_events(replay.text)
        == [e for e in events if e["sequence"] > cursor],
    }
    artifact = {
        "id": case.id,
        "live": True,
        "investigation": saved,
        "evidence": evidence,
        "comparison": comparison,
        "events": events,
        "saved_checks": reads,
        "citation_review": "pending_human_review",
        "elapsed_seconds": time.monotonic() - started,
    }
    if refresh and saved["status"] in {"completed", "partial", "failed"}:
        headers = {"Idempotency-Key": "eval-" + case.id}
        response = await client.post(path + "/refresh", headers=headers)
        response.raise_for_status()
        new_path = response.json()["links"]["self"]
        refreshed = await wait_terminal(client, new_path)
        before = call_count()
        retry = await client.post(path + "/refresh", headers=headers)
        retry.raise_for_status()
        artifact["refresh"] = {
            "investigation": refreshed,
            "evidence": await get_json(client, new_path + "/evidence"),
            "comparison": await get_json(client, new_path + "/comparison"),
            "separate_version": refreshed["id"] != saved["id"],
            "idempotent_retry": retry.json() == refreshed,
            "baseline_unchanged": await get_json(client, path) == saved,
            "zero_provider_calls_on_retry_and_reads": call_count() == before,
        }
    return artifact


def dataset_hash(cases):
    payload = json.dumps([c.model_dump() for c in cases], sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()


# --- Batch evaluation over a claims CSV -------------------------------------------------

CLAIM_COLUMNS = (
    "id",
    "split",
    "claim",
    "case_type",
    "expected_outcome",
    "expected_verdict",
    "unable_reason",
    "what_is_correct",
    "what_needs_correction",
    "corrected_claim",
    "source_url_1",
    "source_shows_1",
    "source_url_2",
    "source_shows_2",
    "as_of",
    "domain",
    "note",
)


class BatchClaim(EvaluationRecord):
    """One labelled claim. Only `claim` ever leaves this record for a research request."""

    id: str = Field(pattern=r"^[a-z][a-z0-9-]{1,39}$")
    split: Literal["tuning", "heldout"]
    claim: str = Field(min_length=10, max_length=500)
    case_type: Literal["direct_fact", "comparison", "causal", "conflict", "insufficient"]
    expected_outcome: Literal["decided", "unable_to_decide"]
    expected_verdict: Literal["true", "false", "almost"] | None
    unable_reason: Literal["insufficient_evidence", "conflicting_evidence"] | None
    what_is_correct: str = ""
    what_needs_correction: str = ""
    corrected_claim: str = ""
    sources: list[KeySource] = Field(max_length=3)
    as_of: str = ""
    domain: str = ""
    note: str = ""

    @model_validator(mode="after")
    def consistent(self):
        decided = self.expected_outcome == "decided"
        if decided != (self.expected_verdict is not None) or decided == (
            self.unable_reason is not None
        ):
            raise ValueError("Inconsistent expected decision")
        InvestigationRequest(claim=self.claim)
        return self

    @property
    def expected(self):
        # Phase 1 scores the statement as written; retain original labels on disk.
        verdict = "false" if self.expected_verdict == "almost" else self.expected_verdict
        return (self.expected_outcome, verdict, self.unable_reason)

    def request(self):
        # Deliberate allowlist: labels, sources and notes never enter prompts.
        return {"claim": self.claim}


def load_claims_csv(path: Path, *, split=None, ids=None):
    import csv

    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != CLAIM_COLUMNS:
            raise ValueError("Unexpected claims CSV columns")
        rows = list(reader)
    claims = []
    for row in rows:
        sources = [
            {"url": row[f"source_url_{n}"], "shows": row[f"source_shows_{n}"]}
            for n in (1, 2)
            if row[f"source_url_{n}"]
        ]
        claims.append(
            BatchClaim(
                **{k: row[k] for k in ("id", "split", "claim", "case_type", "expected_outcome")},
                expected_verdict=row["expected_verdict"] or None,
                unable_reason=row["unable_reason"] or None,
                what_is_correct=row["what_is_correct"],
                what_needs_correction=row["what_needs_correction"],
                corrected_claim=row["corrected_claim"],
                sources=sources,
                as_of=row["as_of"],
                domain=row["domain"],
                note=row["note"],
            )
        )
    return select_claims(claims, split=split, ids=ids)


def claims_from_cases(cases):
    """Reuse reviewed-format JSON cases in a batch (for example a model comparison)."""
    return [
        BatchClaim(
            id=c.id,
            split=c.split,
            claim=c.claim,
            case_type=c.case_type if c.case_type != "interpretive" else "direct_fact",
            expected_outcome=c.expected.outcome,
            expected_verdict=c.expected.verdict,
            unable_reason=c.expected.unable_to_decide_reason,
            sources=[s.model_dump() for s in c.key_sources],
            as_of=c.as_of,
            note=c.reviewer_note,
        )
        for c in cases
    ]


def select_claims(claims, *, split=None, ids=None):
    if not claims:
        raise ValueError("Evaluation requires at least one claim")
    if len({c.id for c in claims}) != len(claims):
        raise ValueError("Duplicate claim IDs")
    keys = [InvestigationRequest.model_validate(c.request()).request_key() for c in claims]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate requests would reuse research")
    if split:
        claims = [c for c in claims if c.split == split]
    if ids:
        missing = set(ids) - {c.id for c in claims}
        if missing:
            raise ValueError("Unknown claim IDs")
        claims = [c for c in claims if c.id in set(ids)]
    if not claims:
        raise ValueError("No claims selected")
    return claims


def end_state(artifact):
    """How one run ended, in one word the report can count."""
    investigation = artifact.get("investigation") or {}
    status = investigation.get("status") or "runner_failed"
    if status == "completed" and investigation.get("method_limitation"):
        return "unsupported_method"
    return status


def score_claim(claim, artifact):
    investigation = artifact.get("investigation") or {}
    result = investigation.get("result") or {}
    actual = decision_key(result) if result else (None, None, None)
    events = artifact.get("events") or []
    calls = Counter(
        e["payload"].get("operation") for e in events if e["type"] == "provider_attempt_finished"
    )
    used = result.get("budget_used") or {}
    return {
        "id": claim.id,
        "split": claim.split,
        "case_type": claim.case_type,
        "arguable_label": claim.id in ARGUABLE_LABELS,
        "expected": "/".join(v for v in claim.expected if v),
        "end_state": end_state(artifact),
        "stop_reason": investigation.get("stop_reason"),
        "actual": "/".join(v for v in actual if v) or "none",
        "match": bool(result) and actual == claim.expected,
        "elapsed_seconds": round(artifact.get("elapsed_seconds") or 0, 1),
        "model_calls": used.get("model", calls.get("model", 0)),
        "search_calls": used.get("search", calls.get("search", 0)),
        "extract_calls": used.get("extract", calls.get("extract", 0)),
        "total_tokens": (result.get("token_usage") or {}).get("total_tokens"),
        "network_attempts": len(artifact.get("network_attempts") or []),
    }


# Audit annotations are evaluator metadata, never research/model inputs.
ARGUABLE_LABELS = frozenset(
    ["a-03", "a-04", "a-05", "a-13", "a-17", "f-16", "x-10"] + [f"x-{n:02}" for n in range(1, 9)]
)
