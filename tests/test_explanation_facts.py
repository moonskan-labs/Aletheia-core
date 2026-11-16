"""Each published explanation unit needs both one fact and full citation support."""

from uuid import UUID

import pytest
from research_fixtures import Providers
from test_research_pipeline import running, submit


class FactProviders(Providers):
    def __init__(self, relation, *, repair=False):
        self.year = 2000 if relation == "supports" else 2001
        self.repair = repair
        super().__init__(
            relation=relation,
            text=f"The Archive opened in {self.year}; the Archive is in Paris.",
        )

    def model_value(self, schema, data):
        value = super().model_value(schema, data)
        if schema == "Synthesis":
            evidence_id = data["evidence"][0]["id"]
            texts = [f"The Archive opened in {self.year}; the Archive is in Paris."]
            if self.repair and data["repair"]:
                assert "non_atomic_explanation" in data["repair"]["failed_conditions"]
                texts = [f"The Archive opened in {self.year}.", "The Archive is in Paris."]
            value["units"] = [{"text": t, "evidence_ids": [evidence_id]} for t in texts]
        if schema in {"ExplanationCheck", "FalseExplanationCheck"}:
            # Both facts are actually present in the cited paragraph. Grounding alone
            # cannot excuse bundling them into one sentence.
            value["supported_units"] = [u["index"] for u in data["units"]]
            value["single_fact_units"] = [0, 1] if len(data["units"]) == 2 else []
        return value


@pytest.mark.parametrize("relation", ["supports", "contradicts"])
async def test_non_atomic_explanation_is_withheld_even_with_supported_citations(settings, relation):
    providers = FactProviders(relation)
    async with running(settings, providers) as (app, client):
        saved = await submit(client)
        assert saved["status"] == "partial"
        assert saved["result"]["verdict"] is None
        assert not saved["result"]["explanation"]
        events = await app.state.storage.events(UUID(saved["id"]))
        rejections = [
            e.payload
            for e in events
            if e.payload.get("failed_conditions") == "non_atomic_explanation"
        ]
        assert len(rejections) == 2
        assert all(e["affected_units"] == "0" for e in rejections)


@pytest.mark.parametrize("relation", ["supports", "contradicts"])
async def test_repair_splits_facts_and_persists_each_sentence_with_its_citation(settings, relation):
    providers = FactProviders(relation, repair=True)
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["status"] == "completed"
        assert saved["result"]["verdict"] == ("true" if relation == "supports" else "false")
        units = saved["result"]["explanation"]
        assert [u["text"] for u in units] == [
            f"The Archive opened in {providers.year}.",
            "The Archive is in Paris.",
        ]
        evidence = (await client.get(saved["links"]["evidence"])).json()["evidence"]
        assert all(u["evidence_ids"] == [evidence[0]["id"]] for u in units)
        assert (await client.get(saved["links"]["self"])).json()["result"]["explanation"] == units
        assert sum(name == "Synthesis" for name, _ in providers.model_inputs) == 2


@pytest.mark.parametrize("bad_indices", [[0, 0], [1]])
async def test_invalid_single_fact_indices_require_a_valid_repair(settings, bad_indices):
    class BadIndices(Providers):
        checks = 0

        def model_value(self, schema, data):
            value = super().model_value(schema, data)
            if schema == "ExplanationCheck":
                self.checks += 1
                if self.checks == 1:
                    value["single_fact_units"] = bad_indices
            return value

    providers = BadIndices()
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["status"] == "completed"
        assert providers.checks == 2


def test_synthesis_can_keep_six_facts_separate():
    from aletheia.task_contracts import Synthesis

    result = Synthesis.model_validate(
        {
            "almost_correction": None,
            "units": [
                {"text": f"Archive {i} opened in 2000.", "evidence_ids": [f"e{i}"]}
                for i in range(6)
            ],
        }
    )
    assert len(result.units) == 6
