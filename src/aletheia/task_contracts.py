"""Compact generation contracts; persisted research records remain backward compatible."""

from typing import Annotated, Literal

from pydantic import Field, create_model

from aletheia import research_contracts as saved
from aletheia.phase_one_contracts import (
    ClaimAnalysis,
    Component,
    ComponentId,
    Method,
    RecordedValue,
)

Brief = Annotated[str, Field(strict=True, min_length=1, max_length=300)]
Label = Annotated[str, Field(strict=True, min_length=1, max_length=160)]


class ClaimPlan(saved.ClaimPlan):
    analysis: ClaimAnalysis
    clarification_reason: (
        Literal["missing_scope", "compound", "non_factual", "factual_uncertainty"] | None
    )


class ClaimInterpretation(saved.Record):
    # The model chooses a method and components; Python owns original wording,
    # assertion IDs, supported/type/scope derivation, and the persisted envelope.
    method: Method
    reason: saved.Short
    components: Annotated[list[Component], Field(min_length=1, max_length=8)]
    missing_scope: Annotated[list[saved.Short], Field(max_length=4)]
    questions: Annotated[list[saved.Short], Field(max_length=4)]
    clarification_reason: Literal["missing_scope", "factual_uncertainty"] | None
    recommended_route: saved.Route
    scope_note: saved.Text


class Citation(saved.Citation):
    span_ids: Annotated[
        list[Annotated[int, Field(strict=True, ge=1)]], Field(min_length=1, max_length=6)
    ]


class ProposedFlag(saved.ProposedFlag):
    explanation: Brief


class Assessment(saved.Assessment):
    component_id: ComponentId
    values: Annotated[list[RecordedValue], Field(max_length=2)]
    citation: Citation
    synthesis_coverage: Brief | None
    publisher: Label | None
    origin: Label | None
    provenance_span_ids: Annotated[
        list[Annotated[int, Field(strict=True, ge=1)]], Field(max_length=6)
    ]
    provenance_note: Brief | None
    rationale: Brief
    limitations: Annotated[list[Brief], Field(max_length=3)]
    flags: Annotated[list[ProposedFlag], Field(max_length=3)]


class AssessmentBatch(saved.AssessmentBatch):
    assessments: Annotated[list[Assessment], Field(max_length=8)]


class RecordAssessment(Assessment):
    # Ordinary fact/date-modifier assessments never need comparison operands.
    values: Annotated[list[RecordedValue], Field(max_length=0)]


# Keep the task's schema name stable while making illegal numeric operands
# unrepresentable in the generation contract for a non-comparison assertion.
RecordAssessmentBatch = create_model(
    "AssessmentBatch",
    __base__=AssessmentBatch,
    assessments=(Annotated[list[RecordAssessment], Field(max_length=8)], ...),
)


class ExplanationUnit(saved.ExplanationUnit):
    text: Brief
    evidence_ids: Annotated[list[saved.Identifier], Field(min_length=1, max_length=6)]


class AlmostCorrection(saved.AlmostCorrection):
    what_is_correct: ExplanationUnit
    what_needs_correction: ExplanationUnit
    corrected_claim: ExplanationUnit


class Synthesis(saved.Synthesis):
    almost_correction: AlmostCorrection | None
    units: Annotated[list[ExplanationUnit], Field(min_length=1, max_length=3)]
