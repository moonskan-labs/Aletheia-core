"""Preserve the submitted claim and distinguish method support from missing scope."""

import re

from aletheia.phase_one_contracts import ClaimAnalysis
from aletheia.research_contracts import Assertion
from aletheia.task_contracts import ClaimInterpretation, ClaimPlan
from aletheia.tasks import TaskValidationError


def validate_claim(plan, original=None):
    if plan.clarification_reason == "factual_uncertainty":
        raise TaskValidationError("factual_uncertainty")
    if plan.questions and (plan.assertions or plan.clarification_reason != "missing_scope"):
        raise TaskValidationError("clarification_shape")
    if not plan.questions and plan.clarification_reason is not None:
        raise TaskValidationError("clear_claim_reason")
    if any(not q.strip() for q in plan.questions) or any(
        not a.text.strip() for a in plan.assertions
    ):
        raise TaskValidationError("blank_claim")
    if not plan.questions and len(plan.assertions) != 1:
        raise TaskValidationError("claim_shape")
    analysis = getattr(plan, "analysis", None)
    if analysis is not None:
        if bool(plan.questions) != (analysis.scope == "missing"):
            raise TaskValidationError("phase_one_scope")
        if original is not None:
            if any(c.text not in original for c in analysis.components):
                raise TaskValidationError("component_text")
            # Dates and quantities in descriptive modifiers cannot disappear during parsing.
            numbers = set(re.findall(r"\b\d+(?:[.,]\d+)*\b", original))
            retained = set(
                re.findall(r"\b\d+(?:[.,]\d+)*\b", " ".join(c.text for c in analysis.components))
            )
            if not numbers <= retained:
                raise TaskValidationError("component_numbers")
            if plan.assertions and plan.assertions[0].text != original:
                raise TaskValidationError("assertion_wording")


_NUMBER = r"\b\d+(?:[.,]\d+)*\b"


def _locate(text, original):
    """Exact substring of the original that matches text, ignoring case and outer spaces."""
    probe = text.strip()
    if not probe:
        return None
    if probe in original:
        return probe
    folded = original.casefold()
    if len(folded) != len(original):
        return None
    start = folded.find(probe.casefold())
    return original[start : start + len(probe)] if start >= 0 else None


def normalize_interpretation(proposal, original):
    """Repair component shape in code; the submitted wording always wins.

    Components the model reworded or invented are not substrings of the claim, so they
    are dropped (a comparison specification is kept and anchored to the whole claim).
    If anything was dropped, no essential component survives, or a number or date from
    the claim is no longer covered, one essential component is widened to the whole
    claim so no part of the proposition is lost. This never adds model text and never
    narrows what must be supported. Method, scope and questions are left to the model
    and to materialize().
    """
    lookup = proposal.method == "record_lookup"
    kept, dropped = [], False
    for component in proposal.components:
        text = _locate(component.text, original)
        comparison = None if lookup else component.comparison
        if text is None:
            if comparison is None:
                dropped = True
                continue
            text = original
        kept.append(component.model_copy(update={"text": text, "comparison": comparison}))
    numbers = set(re.findall(_NUMBER, original))
    retained = set(re.findall(_NUMBER, " ".join(c.text for c in kept)))
    if dropped or not any(c.role == "essential" for c in kept) or not numbers <= retained:
        target = next((c for c in kept if c.role == "essential"), None)
        if target is None:
            target = (kept or list(proposal.components))[0]
            target = target.model_copy(update={"comparison": None if lookup else target.comparison})
            kept = [target] + [c for c in kept if c.id != target.id]
        whole = target.model_copy(update={"text": original, "role": "essential"})
        kept = [whole if c.id == target.id else c for c in kept]
    # One passage must not be assessed twice as both a proposition and its fragment.
    # Keep the longest enclosing text; identical copies retain their original order.
    containers = []
    for index, component in enumerate(kept):
        if any(
            component.text in other.text
            and (len(component.text) < len(other.text) or index > other_index)
            for other_index, other in enumerate(kept)
            if index != other_index
        ):
            continue
        contained = [c for c in kept if c.text in component.text]
        updates = {}
        if any(c.role == "essential" for c in contained):
            updates["role"] = "essential"
        if component.comparison is None:
            comparisons = [c.comparison for c in contained if c.comparison]
            if comparisons:
                updates["comparison"] = comparisons[0]
        containers.append(component.model_copy(update=updates) if updates else component)
    kept = containers
    # Named operands are researchable; do not ask the user to supply their facts.
    named_pair = proposal.method == "record_comparison" and any(
        c.comparison
        and not c.comparison.exhaustive
        and _locate(c.comparison.left, original)
        and _locate(c.comparison.right, original)
        and c.comparison.left.casefold() != c.comparison.right.casefold()
        for c in kept
    )
    if named_pair:
        return proposal.model_copy(
            update={
                "components": kept,
                "questions": [],
                "missing_scope": [],
                "clarification_reason": None,
            }
        )
    if kept == list(proposal.components):
        return proposal
    return proposal.model_copy(update={"components": kept})


def materialize(proposal, original):
    """Build the saved contract without asking the model to copy or derive it."""
    if proposal.method == "record_comparison" and not any(
        c.comparison for c in proposal.components
    ):
        raise TaskValidationError("comparison_missing")
    if proposal.method == "record_lookup" and any(c.comparison for c in proposal.components):
        raise TaskValidationError("comparison_method")
    analysis = ClaimAnalysis(
        primary_type={"record_lookup": "direct_fact", "record_comparison": "direct_comparison"}.get(
            proposal.method, proposal.method
        ),
        required_method=proposal.method,
        supported=proposal.method in {"record_lookup", "record_comparison"},
        scope="missing" if proposal.missing_scope else "complete",
        reason=proposal.reason,
        missing_scope=proposal.missing_scope,
        components=proposal.components,
    )
    plan = ClaimPlan(
        analysis=analysis,
        assertions=[]
        if proposal.questions
        else [
            Assertion(
                text=original,
                kind="direct_record" if analysis.supported else "generalized",
                consequential=proposal.recommended_route == "deep",
                recommended_route=proposal.recommended_route,
                analysis=analysis,
            )
        ],
        questions=proposal.questions,
        clarification_reason=proposal.clarification_reason,
        scope_note=proposal.scope_note,
    )
    validate_claim(plan, original)
    return plan


async def interpret(tasks, investigation):
    proposal = await tasks.call(
        "interpret",
        "Preserve the submitted claim EXACTLY, including all descriptive modifiers, dates, "
        "negation and quantities. Do not correct from memory or decide truth. Choose ONE method; "
        "Python derives support, scope and the saved assertion from your response. Direct facts "
        "use record_lookup; direct comparisons use record_comparison. Copy each operand's "
        "name exactly from the original claim. When both operands are named, do not ask "
        "for clarification: research their separately cited facts. Other types use the "
        "corresponding unsupported method: causal, prediction, counterfactual, "
        "scientific_inference, interpretive or mixed. Topics are metadata, not methods. "
        "An unknown answer or unavailable record is not missing scope. A scientific existence "
        "hypothesis may require inference; a general existence assertion does not need an "
        "invented region or habitat. Do not route by expected truth or search success. "
        "Unsupported claims retain all components, with questions=[] and missing_scope=[] when "
        "scope is complete; never disguise a method limitation as a clarification. Mixed "
        "methods or independent propositions require mixed, never silently drop a part. "
        "Only genuinely missing essential scope permits nonempty questions and missing_scope, "
        "clarification_reason=missing_scope. Identify what the user must supply. Resolve "
        "relative dates only from supplied absolute context. For complete scope use null "
        "clarification_reason. Components must be exact substrings of the original claim, "
        "with c1..c8 IDs, subject, predicate, timeframe, location_or_population, and essential "
        "or modifier role. Separate date modifiers from the main proposition. Components "
        "must collectively retain EVERY material detail. Comparison fields specify both "
        "operands, metric, operator, units, period, population, definition and whether the "
        "claim is an exhaustive superlative. Use explicit 'not applicable' for fields that "
        "do not constrain the comparison; never invent an unspecified period or definition. "
        "A component is a proposition, not an isolated noun or entity. For example, in "
        '"The Museum, opened in 1974, houses the city archive.", the essential component '
        'text is "houses the city archive" (subject: The Museum), and its modifier is '
        '"opened in 1974". Copy these contiguous substrings without adding the subject '
        "or changing capitalization/punctuation; the subject belongs in the subject field. "
        "Causal/efficacy claims (X causes Y, treatment improves Y, policy reduces Y) require "
        "causal even if papers report results or a comparison group is named. A recorded "
        "measurement in a named dataset is record_lookup; attributing an effect to a "
        "treatment is causal. Superlatives and comparisons of recorded values use "
        "record_comparison, with comparison fields. A scientific existence hypothesis "
        "requires scientific_inference. A claim about what a named document says can be "
        "record_lookup even when the document discusses causation. "
        "For superlatives preserve the full comparison set as right; a counterexample can "
        "refute it, but a pair alone cannot prove it. Research depth changes effort only, "
        "never the evidence standard.",
        {"claim": investigation.claim, "context": investigation.context},
        ClaimInterpretation,
        lambda value: materialize(
            normalize_interpretation(value, investigation.claim), investigation.claim
        ),
    )
    proposal = normalize_interpretation(proposal, investigation.claim)
    plan = materialize(proposal, investigation.claim)
    if not plan.analysis.supported or plan.questions:
        reviewed = await tasks.call(
            "review_route",
            "Review the proposed scope and method classification against the ORIGINAL claim. "
            "Do not decide truth or silently correct wording. Missing scope must materially "
            "change the proposition. Unknown truth and unsupported inference are not missing "
            "scope; do not invent regions for a general existence claim. Preserve all material "
            "components and exact original assertion wording. Return the complete corrected "
            "interpretation, or the same interpretation if justified. Explain any changed "
            "classification in reason. Judge the required METHOD rather than the availability "
            "of papers: treatment/policy effects require causal inference; a direct quote "
            "about what a named record states is record_lookup. "
            "No external evidence or expected answer is available.",
            {
                "claim": investigation.claim,
                "context": investigation.context,
                "proposed_plan": proposal.model_dump(),
            },
            ClaimInterpretation,
            lambda value: materialize(
                normalize_interpretation(value, investigation.claim), investigation.claim
            ),
        )
        reviewed = materialize(
            normalize_interpretation(reviewed, investigation.claim), investigation.claim
        )
        if reviewed.analysis != plan.analysis:
            await tasks.emit(
                "route_revised",
                {
                    "previous_method": plan.analysis.required_method,
                    "method": reviewed.analysis.required_method,
                    "previous_scope": plan.analysis.scope,
                    "scope": reviewed.analysis.scope,
                    "reason": reviewed.analysis.reason,
                },
            )
        plan = reviewed
    if plan.assertions:
        plan.assertions[0] = plan.assertions[0].model_copy(
            update={
                "text": investigation.claim,
                "analysis": plan.analysis,
                "kind": "direct_record" if plan.analysis.supported else plan.assertions[0].kind,
            }
        )
    return plan


def route(assertion):
    deep = (
        assertion.recommended_route == "deep"
        or assertion.consequential
        or (not assertion.analysis and assertion.kind != "direct_record")
    )
    return (
        ("deep", "Additional research capacity requested; evidence requirements are unchanged.")
        if deep
        else ("quick", "A precise direct record may settle the claim.")
    )
