"""Passage reading: the model must reason before it labels, and old records must still load.

Measured cause (80 tuning claims, Nov 15): 386 of 558 assessments were labelled `context`
and only 2 were usable contradictions, although many rationales said the passage confirmed
or contradicted the claim. The label was generated before the rationale.
"""

from aletheia.research_contracts import Assessment as SavedAssessment
from aletheia.task_contracts import AssessmentBatch, RecordAssessmentBatch
from aletheia.tasks import PROMPT_VERSION


def assessment_schema(batch):
    definitions = batch.model_json_schema()["$defs"]
    name = next(n for n in definitions if n.endswith("Assessment"))
    return definitions[name]["properties"]


def test_rationale_is_generated_before_the_relation_and_scope_labels():
    for batch in (AssessmentBatch, RecordAssessmentBatch):
        order = list(assessment_schema(batch))
        assert order.index("rationale") < order.index("relation") < order.index("scope_match")


def test_relation_and_scope_fields_tell_the_model_what_a_contradiction_is():
    fields = assessment_schema(RecordAssessmentBatch)
    assert "different value" in fields["relation"]["description"]
    assert "even when the value they give differs" in fields["scope_match"]["description"]
    assert "Write this first" in fields["rationale"]["description"]
    assert PROMPT_VERSION == "direct-claims-v5"


def test_records_saved_in_the_old_field_order_still_load():
    old = {
        "component_id": "c1",
        "values": [],
        "citation": {"snapshot_id": "s1", "span_ids": [1]},
        "relation": "contradicts",
        "scope_match": True,
        "authoritative_record": True,
        "credible_synthesis": False,
        "synthesis_coverage": None,
        "publisher": None,
        "origin": None,
        "independence": "unknown",
        "provenance_span_ids": [],
        "provenance_note": None,
        "rationale": "The page gives 2001, not 2000.",
        "limitations": [],
        "flags": [],
    }
    assert SavedAssessment.model_validate(old).relation == "contradicts"
