"""Only validated, non-repeated queries can reach search."""

from aletheia.research_contracts import SearchPlan
from aletheia.tasks import TaskValidationError


def query_key(text):
    return " ".join(text.casefold().split())


def fit_plan(plan, seen, initial, capacity=3):
    """Trim a proposal in code so a fixable shape error does not cost a repair call.

    Blank, repeated and already-searched queries are dropped, then the list is cut to
    the remaining search capacity. Model wording is never rewritten and nothing is
    added, so validate_plan still decides whether the fitted plan is acceptable.
    """
    capacity = max(0, capacity)
    queries, keys = [], set(seen)
    for query in plan.queries:
        key = query_key(query.text)
        if key and key not in keys:
            keys.add(key)
            queries.append(query)
    if len(queries) > capacity:
        # Keep counterevidence coverage when two or more searches remain.
        keep = []
        if capacity >= 2:
            for purpose in ("support", "contradiction"):
                first = next((q for q in queries if q.purpose == purpose), None)
                if first is not None:
                    keep.append(first)
        keep += [q for q in queries if all(q is not k for k in keep)]
        keep = keep[:capacity]
        queries = [q for q in queries if any(q is k for k in keep)]
    if len(queries) == len(plan.queries):
        return plan
    return plan.model_copy(update={"queries": queries})


def validate_plan(plan, seen, initial, capacity=3):
    if len(plan.queries) > max(0, capacity):
        raise TaskValidationError("query_capacity")
    keys = [query_key(q.text) for q in plan.queries]
    if any(not key or key in seen for key in keys) or len(set(keys)) != len(keys):
        raise TaskValidationError("query_identity")
    if (
        initial
        and capacity >= 2
        and plan.queries
        and not {"support", "contradiction"} <= {q.purpose for q in plan.queries}
    ):
        raise TaskValidationError("query_coverage")
    if not initial and plan.queries and (not plan.gap or not plan.gap.strip()):
        raise TaskValidationError("query_gap")


async def plan_search(tasks, assertion, route, seen, gap=None, evidence_context=None):
    fitted = []

    def check(value):
        capacity = tasks.budget.search_attempts - tasks.budget.used["search"]
        plan = fit_plan(value, seen, gap is None, capacity)
        validate_plan(plan, seen, gap is None, capacity)
        fitted.append(plan)

    await tasks.call(
        "plan",
        "Propose at most three precise search queries for a1. A nonempty initial plan MUST include "
        "both support and contradiction searches; look for primary records and corrections. "
        "Follow-up queries must address the named evidence gap and must not repeat previous "
        "queries. Use the supplied evidence summaries to target missing scope, original sources "
        "and disagreements. Summaries may be truncated; rejected evidence contributes metadata "
        "only. These are search leads, not new evidence. Stay within remaining search and "
        "extraction attempts. "
        "Return no queries if there is no useful new search. Never use prior verdicts.",
        {
            "assertion": assertion.model_dump(),
            "route": route,
            "gap": gap,
            "previous_queries": sorted(seen),
            "remaining_search_attempts": tasks.budget.search_attempts - tasks.budget.used["search"],
            "remaining_extraction_attempts": tasks.budget.extraction_attempts
            - tasks.budget.used["extract"],
            "remaining_research_model_attempts": tasks.budget.model_attempts
            - tasks.budget.reserve_model_attempts
            - tasks.budget.used["model"],
            "remaining_research_seconds": tasks.budget.remaining_seconds(),
            "evidence_context": evidence_context or {"summaries": [], "omitted_assessments": 0},
        },
        SearchPlan,
        check,
    )
    return fitted[-1]
