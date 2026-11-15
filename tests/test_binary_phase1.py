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


@pytest.mark.parametrize("confirmed", [True, False])
async def test_false_check_asks_about_falsity_and_can_still_withhold(settings, confirmed):
    from aletheia.verdicts import FalseExplanationCheck

    class Checker(Providers):
        def model_value(self, schema, data):
            result = super().model_value(schema, data)
            if schema == "FalseExplanationCheck":
                result["claim_is_false"] = confirmed
            return result

    fields = FalseExplanationCheck.model_json_schema()["properties"]
    assert "rejected_component_ids" not in fields
    assert "decision_supported" not in fields
    assert "claim is false" in fields["claim_is_false"]["description"]
    providers = Checker(relation="contradicts")
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["result"]["verdict"] == ("false" if confirmed else None)
        assert saved["status"] == ("completed" if confirmed else "partial")
        names = [name for name, _ in providers.model_inputs]
        assert names.count("FalseExplanationCheck") == (1 if confirmed else 2)


def test_contained_components_are_removed_without_losing_scope_or_essential_role():
    from test_demo_reliability import interpretation

    from aletheia.claims import materialize, normalize_interpretation

    text = "The Archive opened in 2000 in Paris."
    proposal = interpretation(
        [
            ("opened in 2000", "essential", None),
            (text, "modifier", None),
            ("Paris", "modifier", None),
            (text, "modifier", None),
        ]
    )
    fixed = normalize_interpretation(proposal, text)
    assert len(fixed.components) == 1
    assert fixed.components[0].text == text
    assert fixed.components[0].role == "essential"
    materialize(fixed, text)


@pytest.mark.parametrize(
    "support_strong,contra_strong,expected",
    [
        (True, False, "true"),
        (False, True, "false"),
        (True, True, None),
        (False, False, None),
    ],
)
def test_conflicts_require_both_sides_to_meet_evidence_rule(
    support_strong, contra_strong, expected
):
    from test_phase_one import assertion
    from test_research_integrity import judgment, source

    from aletheia.evidence import admit
    from aletheia.verdicts import finding

    claim = assertion("The Archive opened in 2000.")
    sources = [source("The Archive opened in 2000."), source("It opened in 2001.")]
    evidence = [
        admit(
            judgment(s, component_id="c1", relation=relation, authoritative_record=strong), s, {1}
        )
        for s, relation, strong in zip(
            sources, ["supports", "contradicts"], [support_strong, contra_strong], strict=True
        )
    ]
    result, _ = finding(claim, "quick", evidence, sources)
    assert result.verdict == expected
    assert (result.unable_to_decide_reason == "conflicting_evidence") == (
        support_strong and contra_strong
    )
    assert len(result.components[0].evidence_ids) == 2


def test_weak_comparison_counterexample_does_not_veto_grounded_operands():
    from test_phase_one import assertion, comparison_spec, value
    from test_research_integrity import judgment, source

    from aletheia.evidence import admit
    from aletheia.verdicts import finding

    claim = assertion(
        "Venus is closer than Mercury.", kind="direct_comparison", comparison=comparison_spec()
    )
    sources, evidence = [], []
    for side, number, strong in [
        ("left", "108", True),
        ("right", "58", True),
        ("right", "200", False),
    ]:
        s = source(number)
        sources.append(s)
        evidence.append(
            admit(
                judgment(
                    s,
                    component_id="c1",
                    relation="context",
                    values=[value(side, number)],
                    authoritative_record=strong,
                ),
                s,
                {1},
            )
        )
    assert finding(claim, "quick", evidence, sources)[0].verdict == "false"
    evidence[-1].assessment.authoritative_record = True
    assert (
        finding(claim, "quick", evidence, sources)[0].unable_to_decide_reason
        == "conflicting_evidence"
    )
