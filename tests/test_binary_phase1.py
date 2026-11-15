"""Current production Phase 1 rules, without the historical Almost test override."""

import pytest
from research_fixtures import Providers
from test_batch_eval import CLAIMS, claim
from test_research_pipeline import running, submit

from aletheia.evaluation import ARGUABLE_LABELS, load_claims_csv, score_claim
from aletheia.verdicts import ALMOST_ENABLED


@pytest.mark.parametrize(
    "relation,verdict", [("supports", "true"), ("contradicts", "false"), ("context", None)]
)
async def test_phase1_drops_even_a_valid_almost_proposal(settings, relation, verdict):
    assert ALMOST_ENABLED is False
    providers = Providers(almost=True, relation=relation)
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["status"] == "completed"
        assert saved["result"]["verdict"] == verdict
        assert saved["result"]["almost_correction"] is None
        synthesis_inputs = [data for name, data in providers.model_inputs if name == "Synthesis"]
        assert len(synthesis_inputs) == 1
        assert synthesis_inputs[0]["almost_eligible"] is False


def test_almost_label_scores_as_false_without_changing_the_label():
    item = claim(expected_verdict="almost")
    artifact = {
        "investigation": {
            "status": "completed",
            "result": {
                "outcome": "decided",
                "verdict": "false",
                "unable_to_decide_reason": None,
            },
        }
    }
    assert score_claim(item, artifact)["match"] is True
    assert item.expected_verdict == "almost"
    artifact["investigation"]["result"]["verdict"] = "almost"
    assert score_claim(item, artifact)["match"] is False


def test_audit_scoring_keeps_arguable_labels_and_corrects_c01():
    claims = {item.id: item for item in load_claims_csv(CLAIMS)}
    assert claims["c-01"].expected == ("decided", "true", None)
    assert len(ARGUABLE_LABELS) == 15
    assert sum(claims[i].split == "tuning" for i in ARGUABLE_LABELS) == 11
    assert claims["a-03"].expected_verdict == "almost"
    assert score_claim(claims["a-03"], {})["arguable_label"] is True
