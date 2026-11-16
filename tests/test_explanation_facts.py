"""Each published explanation unit needs both one fact and full citation support.

The decision question alone gates the verdict; a failed sentence is removed or replaced
by the cited passage, and never removes a verdict the check confirmed.
"""

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
async def test_bundled_sentence_is_never_published_but_the_confirmed_verdict_stays(
    settings, relation
):
    providers = FactProviders(relation)
    async with running(settings, providers) as (app, client):
        saved = await submit(client)
        assert saved["status"] == "completed"
        assert saved["result"]["verdict"] == ("true" if relation == "supports" else "false")
        passage = f"The Archive opened in {providers.year}; the Archive is in Paris."
        # The bundled sentence failed twice, so the cited passage is quoted instead.
        assert [u["text"] for u in saved["result"]["explanation"]] == [
            f'The cited source states: "{passage}"'
        ]
        assert any("quoted directly" in note for note in saved["result"]["limitations"])
        events = await app.state.storage.events(UUID(saved["id"]))
        assert [
            e.payload["action"] for e in events if e.payload.get("task") == "explanation_unit"
        ] == ["quoted_passages"]
        assert sum(name == "Synthesis" for name, _ in providers.model_inputs) == 2


class TwoSentences(Providers):
    """Two explanation sentences; the checker's answers are set per test."""

    def __init__(self, *, supported, decision=(True, True), **options):
        self.supported, self.decision, self.checks = supported, decision, 0
        super().__init__(**options)

    def model_value(self, schema, data):
        value = super().model_value(schema, data)
        if schema == "Synthesis":
            evidence_id = data["evidence"][0]["id"]
            value["units"] = [
                {"text": text, "evidence_ids": [evidence_id]}
                for text in ("The Archive opened in 2000.", "The Archive won a prize.")
            ]
        if schema in {"ExplanationCheck", "FalseExplanationCheck"}:
            value["supported_units"] = self.supported
            value["single_fact_units"] = [0, 1]
            answer = self.decision[min(self.checks, 1)]
            self.checks += 1
            key = "claim_is_false" if schema == "FalseExplanationCheck" else "decision_supported"
            value[key] = answer
        return value


async def test_unsupported_sentence_is_dropped_without_a_second_attempt(settings):
    providers = TwoSentences(supported=[0])
    async with running(settings, providers) as (app, client):
        saved = await submit(client)
        assert saved["status"] == "completed" and saved["result"]["verdict"] == "true"
        assert [u["text"] for u in saved["result"]["explanation"]] == [
            "The Archive opened in 2000."
        ]
        assert not any("quoted directly" in note for note in saved["result"]["limitations"])
        events = await app.state.storage.events(UUID(saved["id"]))
        dropped = [e.payload for e in events if e.payload.get("task") == "explanation_unit"]
        assert [(d["action"], d["affected_units"]) for d in dropped] == [("dropped", "1")]
        assert providers.checks == 1


@pytest.mark.parametrize("relation", ["supports", "contradicts"])
async def test_good_prose_cannot_publish_a_decision_the_check_did_not_confirm(settings, relation):
    providers = TwoSentences(supported=[0, 1], decision=(False, False), relation=relation)
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["status"] == "partial" and saved["stop_reason"] == "semantic_rejection"
        assert saved["result"]["verdict"] is None
        assert not saved["result"]["explanation"]
        assert providers.checks == 2


async def test_a_confirmed_decision_is_not_asked_again_while_prose_is_repaired(settings):
    # First check: decision yes, no sentence passes. Second check answers no to the
    # decision, but that question was already settled against the same evidence.
    providers = TwoSentences(supported=[], decision=(True, False))
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["status"] == "completed" and saved["result"]["verdict"] == "true"
        assert saved["result"]["explanation"][0]["text"].startswith("The cited source states:")
        assert providers.checks == 2


async def test_unable_to_decide_never_gains_a_verdict_or_quotes_from_the_prose_check(settings):
    providers = TwoSentences(supported=[], scope_match=False)
    async with running(settings, providers) as (_, client):
        saved = await submit(client)
        assert saved["result"]["verdict"] is None
        assert not saved["result"]["explanation"]


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
