"""Deterministic repairs for the two non-selection replay stops.

The component shapes below are copied from saved replay proposals
(experiments/pipeline-replay-20261111): every one failed interpretation there.
"""

import pytest

from aletheia.claims import materialize, normalize_interpretation
from aletheia.planning import fit_plan, validate_plan
from aletheia.research_contracts import SearchPlan
from aletheia.task_contracts import ClaimInterpretation
from aletheia.tasks import TaskValidationError

VENUS = "Venus is the closest planet to the Sun."
SHA = "The SHA-256 cryptographic hash algorithm produces a 256-bit digest."
PYTHON = (
    "The original version of the Python programming language was first publicly released in 2001."
)
PARIS = "The Paris Agreement was adopted at the United Nations climate conference in December 2015."

COMPARISON = {
    "left": "Venus",
    "right": "all planets",
    "metric": "distance from the Sun",
    "operator": "lt",
    "units": "not applicable",
    "period": "not applicable",
    "population": "planets",
    "definition": "not applicable",
    "exhaustive": True,
}


def interpretation(components, method="record_lookup"):
    return ClaimInterpretation.model_validate(
        {
            "method": method,
            "reason": "Recorded fact.",
            "components": [
                {
                    "id": f"c{index}",
                    "text": text,
                    "role": role,
                    "subject": "subject",
                    "predicate": "predicate",
                    "timeframe": None,
                    "location_or_population": None,
                    "comparison": comparison,
                }
                for index, (text, role, comparison) in enumerate(components, 1)
            ],
            "missing_scope": [],
            "questions": [],
            "clarification_reason": None,
            "recommended_route": "quick",
            "scope_note": "Complete.",
        }
    )


REPLAY_FAILURES = [
    (
        VENUS,
        [
            ("Venus is the closest planet to the Sun", "essential", None),
            ("Mercury is the closest planet to the Sun", "modifier", None),
        ],
        "component_text",
    ),
    (
        SHA,
        [
            ("SHA-256 produces a 256-bit digest", "essential", None),
            ("cryptographic hash algorithm", "modifier", None),
        ],
        "component_text",
    ),
    (
        PYTHON,
        [
            ("The original version of the Python programming language", "essential", None),
            ("first publicly released", "modifier", None),
        ],
        "component_numbers",
    ),
    (
        PARIS,
        [
            ("The Paris Agreement was adopted", "essential", None),
            ("at the United Nations climate conference", "modifier", None),
        ],
        "component_numbers",
    ),
    (
        VENUS,
        [
            ("Venus is the closest planet to the Sun.", "essential", None),
            ("closest planet to the Sun", "modifier", COMPARISON),
        ],
        "comparison_method",
    ),
]


@pytest.mark.parametrize("claim,components,code", REPLAY_FAILURES)
def test_saved_replay_interpretations_fail_raw_and_pass_after_normalization(
    claim, components, code
):
    proposal = interpretation(components)
    with pytest.raises(TaskValidationError) as error:
        materialize(proposal, claim)
    assert error.value.code == code

    plan = materialize(normalize_interpretation(proposal, claim), claim)
    assert plan.assertions[0].text == claim
    assert all(c.text in claim for c in plan.analysis.components)
    assert any(c.role == "essential" for c in plan.analysis.components)
    assert plan.analysis.required_method == "record_lookup"


def test_invented_component_is_dropped_not_rewritten():
    proposal = interpretation(REPLAY_FAILURES[0][1])
    fixed = normalize_interpretation(proposal, VENUS)
    assert [c.text for c in fixed.components] == [VENUS]


def test_dropping_a_reworded_proposition_never_leaves_only_a_noun_fragment():
    # Saved replay shape: the proposition was reworded and only "256-bit digest" matched.
    proposal = interpretation(
        [
            ("SHA-256 produces a 256-bit digest", "essential", None),
            ("256-bit digest", "essential", None),
        ]
    )
    fixed = normalize_interpretation(proposal, SHA)
    assert [c.text for c in fixed.components] == [SHA]


def test_dropped_number_widens_an_essential_component_to_the_whole_claim():
    fixed = normalize_interpretation(interpretation(REPLAY_FAILURES[2][1]), PYTHON)
    assert fixed.components[0].text == PYTHON and fixed.components[0].role == "essential"
    assert fixed.components[1].text == "first publicly released"


def test_corrected_from_memory_component_falls_back_to_submitted_wording():
    claim = "The Archive opened in 2000."
    fixed = normalize_interpretation(
        interpretation([("The Archive opened in 2001.", "essential", None)]), claim
    )
    assert [c.text for c in fixed.components] == [claim]


def test_valid_interpretation_is_returned_unchanged():
    proposal = interpretation(
        [
            ("The Paris Agreement was adopted", "essential", None),
            ("at the United Nations climate conference in December 2015", "modifier", None),
        ]
    )
    assert normalize_interpretation(proposal, PARIS) is proposal


def test_comparison_specification_survives_reworded_text():
    proposal = interpretation(
        [("Venus is closer to the Sun than every planet", "essential", COMPARISON)],
        method="record_comparison",
    )
    fixed = normalize_interpretation(proposal, VENUS)
    assert fixed.components[0].text == VENUS and fixed.components[0].comparison is not None
    assert materialize(fixed, VENUS).analysis.primary_type == "direct_comparison"


def test_method_and_questions_are_never_changed():
    proposal = interpretation(REPLAY_FAILURES[0][1], method="causal")
    fixed = normalize_interpretation(proposal, VENUS)
    assert fixed.method == "causal" and fixed.questions == []


def plan(*queries, gap=None):
    return SearchPlan.model_validate(
        {
            "queries": [
                {"assertion_id": "a1", "text": text, "purpose": purpose}
                for text, purpose in queries
            ],
            "gap": gap,
        }
    )


def test_followup_over_capacity_is_trimmed_instead_of_rejected():
    proposal = plan(("a", "support"), ("b", "contradiction"), ("c", "context"), gap="date")
    with pytest.raises(TaskValidationError) as error:
        validate_plan(proposal, set(), False, capacity=1)
    assert error.value.code == "query_capacity"

    fitted = fit_plan(proposal, set(), False, capacity=1)
    assert [q.text for q in fitted.queries] == ["a"]
    validate_plan(fitted, set(), False, capacity=1)


def test_trim_keeps_support_and_contradiction_when_two_searches_remain():
    proposal = plan(("a", "support"), ("b", "context"), ("c", "contradiction"))
    fitted = fit_plan(proposal, set(), True, capacity=2)
    assert [q.text for q in fitted.queries] == ["a", "c"]
    validate_plan(fitted, set(), True, capacity=2)


def test_repeated_and_blank_queries_are_dropped():
    proposal = plan(("Old Query", "support"), ("new", "support"), ("NEW ", "context"), gap="g")
    with pytest.raises(TaskValidationError) as error:
        validate_plan(proposal, {"old query"}, False)
    assert error.value.code == "query_identity"

    fitted = fit_plan(proposal, {"old query"}, False)
    assert [q.text for q in fitted.queries] == ["new"]
    validate_plan(fitted, {"old query"}, False)


def test_no_capacity_yields_an_empty_plan_and_fitting_plan_is_untouched():
    proposal = plan(("a", "support"), ("b", "contradiction"))
    assert fit_plan(proposal, set(), True, capacity=0).queries == []
    assert fit_plan(proposal, set(), True, capacity=3) is proposal


def test_fitting_never_invents_missing_counterevidence():
    fitted = fit_plan(plan(("a", "support"), ("b", "support")), set(), True, capacity=3)
    with pytest.raises(TaskValidationError) as error:
        validate_plan(fitted, set(), True, capacity=3)
    assert error.value.code == "query_coverage"
