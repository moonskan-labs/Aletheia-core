"""Live-pilot failure boundaries, with offline HTTP and persisted public results."""

import json
from collections import Counter

import pytest
from pydantic import ValidationError
from research_fixtures import Providers
from test_research_pipeline import running, submit

from aletheia.claims import materialize
from aletheia.task_contracts import ClaimInterpretation, RecordAssessmentBatch
from aletheia.tasks import TaskValidationError


def proposal(claim="The Archive opened in 2000."):
    return ClaimInterpretation.model_validate(
        Providers().model_value("ClaimInterpretation", {"claim": claim})
    )


def test_model_cannot_rewrite_original_or_assign_derived_route_fields():
    claim = "The Archive, opened in 2000, holds maps."
    candidate = proposal(claim)
    plan = materialize(candidate, claim)
    assert plan.assertions[0].text == claim
    assert plan.analysis.required_method == "record_lookup"
    assert plan.analysis.primary_type == "direct_fact" and plan.analysis.supported
    for key, value in [("assertions", []), ("supported", False), ("primary_type", "causal")]:
        with pytest.raises(ValidationError):
            ClaimInterpretation.model_validate({**candidate.model_dump(), key: value})


@pytest.mark.parametrize(
    "method",
    ["causal", "prediction", "counterfactual", "scientific_inference", "interpretive", "mixed"],
)
def test_unsupported_method_does_not_require_contradictory_derived_model_fields(method):
    candidate = proposal()
    candidate.method = method
    plan = materialize(candidate, candidate.components[0].text)
    assert not plan.analysis.supported
    assert plan.analysis.primary_type == method == plan.analysis.required_method
    assert plan.questions == [] and plan.analysis.scope == "complete"


@pytest.mark.parametrize(
    "text,code",
    [
        ("The Archive opened in 2001.", "component_text"),
        ("The Archive opened", "component_numbers"),
    ],
)
def test_repair_code_distinguishes_changed_text_from_dropped_numeric_modifier(text, code):
    candidate = proposal()
    candidate.components[0].text = text
    with pytest.raises(TaskValidationError) as error:
        materialize(candidate, "The Archive opened in 2000.")
    assert error.value.code == code


def test_comparison_route_cannot_omit_its_operands_contract():
    candidate = proposal()
    candidate.method = "record_comparison"
    with pytest.raises(TaskValidationError) as error:
        materialize(candidate, candidate.components[0].text)
    assert error.value.code == "comparison_missing"


def test_fact_generation_schema_excludes_numeric_operands_even_for_date_claims():
    schema = RecordAssessmentBatch.model_json_schema()
    ref = schema["properties"]["assessments"]["items"]["$ref"].split("/")[-1]
    assert schema["$defs"][ref]["properties"]["values"]["maxItems"] == 0


async def test_two_sources_each_get_one_repair_without_spending_finalization_reserve(settings):
    class RepairEach(Providers):
        def __init__(self):
            super().__init__(source_count=2)
            self.assessments = Counter()
            self.instructions = []

        async def handle(self, request):
            if request.url.path.endswith("completions"):
                self.instructions.append(json.loads(request.content)["messages"][0]["content"])
            return await super().handle(request)

        def model_value(self, schema, data):
            value = super().model_value(schema, data)
            if schema == "AssessmentBatch":
                self.assessments[data["snapshot_id"]] += 1
                if self.assessments[data["snapshot_id"]] == 1:
                    value["assessments"][0]["citation"]["span_ids"] = [9999]
            return value

    providers = RepairEach()
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["status"] == "completed" and saved["result"]["verdict"] == "true"
        assert saved["result"]["budget_used"]["model"] == 8
        evidence = (await client.get(saved["links"]["evidence"])).json()["evidence"]
        assert len(evidence) == 2
        assert list(providers.assessments.values()) == [2, 2]
        assert sum("Use only supplied span IDs" in s for s in providers.instructions) == 2
        calls = len(providers.calls)
        assert (await client.get(saved["links"]["self"])).json() == saved
        assert len(providers.calls) == calls
