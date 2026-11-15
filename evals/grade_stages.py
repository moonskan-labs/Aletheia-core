"""Score one backend run per stage, so a failure points to its cause.

Layer A of the backend eval: deterministic, free, standard library only.

    python evals/grade_stages.py <run_dir> --cases <cases.json> [--keys evals/stage-keys]

<run_dir> holds one artifact per case, `<id>.json`, as written by Skanda's
scripts/evaluate_research.py (directly, or in a per-case child directory
`<id>/<id>.json` as written by scripts/rerun_phase_one_pilot.py). <cases.json>
is a list of claim records in the evals/ format; only `id`, `case_type`,
`expected`, `acceptable_alternatives`, `expected_flags` and `key_sources` are
read, and records without labels are graded up to the final-answer stage.
Writes <run_dir>/stage-results.json and prints a one-line funnel.

Each stage is True (passed), False (failed), or None (not gradable: no key
for it yet, or an earlier stage failed). A case's drop-out stage is the first
False. Nothing here changes or imports backend code.
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

STAGES = (
    "ran",
    "interpretation",
    "search_selected",
    "extracted",
    "passage_selection",
    "assessment",
    "final_answer",
    "citations",
)
# Stages 2-4 trace the key source; they are skipped for cases the backend should decline.
SOURCE_STAGES = ("search_selected", "extracted", "passage_selection", "assessment")
QUOTE_MATCH = 0.9  # share of a decisive quote's words that must appear in one excerpt
REJECTION_EVENTS = {
    "task_output_rejected",
    "assessment_rejected",
    "source_rejected",
    "search_incomplete",
    "budget_reached",
    "investigation_failed",
}


# ---------- normalization ----------


def normalize_url(url):
    """Compare URLs by host and path: scheme, www., fragment, tracking query and / ignored."""
    if not url:
        return ""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.").removeprefix("m.")
    path = re.sub(r"/+$", "", parts.path) or ""
    query = "&".join(
        q for q in parts.query.split("&") if q and not q.lower().startswith(("utm_", "fbclid"))
    )
    return host + path + ("?" + query if query else "")


def words(text):
    text = unicodedata.normalize("NFKC", text or "").lower()
    text = text.translate(str.maketrans("‘’“”–—", "''\"\"--"))
    return re.findall(r"[a-z0-9]+(?:[.,'][a-z0-9]+)*", text)


def quote_found(quote, text):
    """True when the quote, or nearly all of its words, appear within one stretch of the text.

    Tolerates the splitter's whitespace, markdown and punctuation changes and a word or two
    of difference; a quote's words scattered across a long page do not count.
    """
    q, t = words(quote), words(text)
    if not q:
        return False
    if " ".join(q) in " ".join(t):
        return True
    need = max(1, round(QUOTE_MATCH * len(q)))
    window = len(q) + max(2, len(q) // 5)
    want = Counter(q)
    return any(
        sum((want & Counter(t[start : start + window])).values()) >= need
        for start in range(max(1, len(t) - window + 1))
    )


# ---------- reading the artifact ----------


def events_of(artifact, kind):
    return [e for e in artifact.get("events", []) if e.get("type") == kind]


def decision_key(decision):
    return tuple((decision or {}).get(k) for k in ("outcome", "verdict", "unable_to_decide_reason"))


def usage(artifact):
    totals = {"prompt_tokens": 0, "completion_tokens": 0}
    for event in events_of(artifact, "task_finished"):
        for key in totals:
            value = str(event.get("payload", {}).get(key, ""))
            if value.isdigit():
                totals[key] += int(value)
    calls = Counter(a.get("provider") for a in artifact.get("network_attempts", []))
    return {**totals, "nebius_calls": calls.get("nebius", 0), "tavily_calls": calls.get("tavily", 0)}


def likely_cause(artifact):
    investigation = artifact.get("investigation") or {}
    last = None
    for event in artifact.get("events", []):
        if event.get("type") in REJECTION_EVENTS:
            payload = event.get("payload", {})
            detail = payload.get("task") or payload.get("reason") or ""
            last = event["type"] + (f":{detail}" if detail else "")
    return {
        "status": investigation.get("status", "runner_failed"),
        "stop_reason": investigation.get("stop_reason") or artifact.get("runner_error"),
        "last_rejection": last,
    }


# ---------- grading ----------


def grade_case(case, artifact, keys=None):
    """Return {"id", "stages": {stage: True|False|None}, "detail", "dropped_at", ...}."""
    keys = keys or {}
    stages = dict.fromkeys(STAGES)
    detail = {}
    investigation = artifact.get("investigation") or {}
    result = investigation.get("result") or {}
    status = investigation.get("status")
    stop_reason = investigation.get("stop_reason")
    expected_route = keys.get("expected_route", "research")
    declined = stop_reason == "unsupported_method" or bool(investigation.get("method_limitation"))

    # 0. Ran
    stages["ran"] = bool(investigation) and not artifact.get("runner_error")
    if not stages["ran"]:
        return finish(case, artifact, stages, detail, expected_route, declined)

    # 1. Interpretation (and the research-or-decline route)
    interpreted = bool(events_of(artifact, "claim_interpreted"))
    detail["needs_clarification"] = status == "needs_clarification"
    if expected_route == "decline":
        stages["interpretation"] = declined
        detail["route"] = "declined" if declined else "researched_instead_of_declining"
        return finish(case, artifact, stages, detail, expected_route, declined)
    if declined:
        stages["interpretation"] = False
        detail["route"] = "declined_a_researchable_claim"
        return finish(case, artifact, stages, detail, expected_route, declined)
    stages["interpretation"] = interpreted and status != "needs_clarification"
    if not stages["interpretation"]:
        return finish(case, artifact, stages, detail, expected_route, declined)

    # 2-4 follow the key sources; they stop where that trail ends. The answer and citations
    # are graded regardless, since a run can answer well from sources nobody listed.
    trace_key_sources(case, artifact, keys, stages, detail)
    return grade_answer(case, artifact, stages, detail, expected_route, declined)


def site_of(url):
    return normalize_url(url).split("/", 1)[0]


def key_source_index(key_sources):
    """Map a URL to the key source it belongs to, by exact URL first, then by accepted site.

    A sidecar key source lists `urls` (exact pages, mirrors) and optionally `sites`
    (hosts whose every page counts, e.g. "unfccc.int"). Without `sites`, the hosts of
    its `urls` count, so the official PDF on the same site as the listed landing page
    still counts as finding the key source. A sidecar sets `"sites": []` to require
    an exact page.
    """
    exact = {normalize_url(u): i for i, k in enumerate(key_sources) for u in k.get("urls", [])}
    sites = {
        s.lower().removeprefix("www."): i
        for i, k in enumerate(key_sources)
        for s in k.get("sites", [site_of(u) for u in k.get("urls", [])])
    }

    def match(url):
        u = normalize_url(url)
        if u in exact:
            return exact[u]
        host = site_of(url)
        return next((i for s, i in sites.items() if host == s or host.endswith("." + s)), None)

    return match


def trace_key_sources(case, artifact, keys, stages, detail):
    key_sources = keys.get("key_sources") or [
        {"urls": [k["url"]]} for k in case.get("key_sources", [])
    ]
    match = key_source_index(key_sources)
    selected = [e["payload"].get("url") for e in events_of(artifact, "source_selected")]
    hits = {match(u) for u in selected} - {None}
    stages["search_selected"] = bool(hits)
    detail["key_sources_selected"] = len(hits)
    detail["pages_selected"] = len(set(selected))
    if not hits:
        return

    evidence = artifact.get("evidence") or {}
    extracted = {
        s["id"]: match(s.get("url")) for s in evidence.get("sources", []) if match(s.get("url")) in hits
    }
    stages["extracted"] = bool(extracted)
    if not extracted:
        return
    detail["key_source_truncated"] = any(
        "truncated" in str(x)
        for s in evidence.get("sources", []) if s["id"] in extracted
        for x in s.get("limitations", [])
    )

    if not any(key_sources[i].get("decisive_quotes") for i in set(extracted.values())):
        detail["passage_key"] = "missing"  # passage and assessment stay ungraded (None)
        return
    decisive = []
    for item in (artifact.get("evidence") or {}).get("evidence", []):
        snapshot = item.get("assessment", {}).get("citation", {}).get("snapshot_id")
        if snapshot not in extracted:
            continue
        source = key_sources[extracted[snapshot]]
        text = " ".join(x.get("text", "") for x in item.get("excerpts", []))
        if any(quote_found(q, text) for q in source.get("decisive_quotes", [])):
            decisive.append((item, source))
    stages["passage_selection"] = bool(decisive)
    if not decisive:
        return
    detail["decisive_relations"] = sorted(
        {
            f"{i['assessment'].get('relation')}/"
            + ("admissible" if i.get("admissible") else str(i.get("rejection_reason")))
            for i, _ in decisive
        }
    )
    stages["assessment"] = any(
        item.get("admissible")
        and source.get("expected_relation") in (None, item["assessment"].get("relation"))
        for item, source in decisive
    )


def grade_answer(case, artifact, stages, detail, expected_route, declined):
    investigation = artifact.get("investigation") or {}
    result = investigation.get("result") or {}
    completed = investigation.get("status") == "completed" and result.get("outcome") in {
        "decided",
        "unable_to_decide",
    }
    detail["completed"] = completed
    decisions = [case["expected"], *case.get("acceptable_alternatives", [])] if case.get("expected") else []
    if decisions:
        stages["final_answer"] = completed and any(
            decision_key(result) == decision_key(d) for d in decisions
        )
        actual = {(f["type"], f["dimension"]) for f in result.get("finding", {}).get("qualification_flags", [])}
        expected = {(f["type"], f["dimension"]) for f in case.get("expected_flags", [])}
        detail["flags"] = {"tp": len(actual & expected), "fp": len(actual - expected), "fn": len(expected - actual)}
        if stages["final_answer"] and result.get("verdict") == "almost":
            detail["almost_correction"] = "needs_judge"
    elif completed:
        detail["final_answer"] = "unlabeled"
    else:
        stages["final_answer"] = False

    sentences = result.get("explanation") or []
    if sentences:
        by_id = {e["id"]: e for e in (artifact.get("evidence") or {}).get("evidence", [])}
        valid = [
            bool(s.get("evidence_ids"))
            and all(by_id.get(i, {}).get("admissible") for i in s["evidence_ids"])
            for s in sentences
        ]
        stages["citations"] = all(valid)
        detail["citations_valid"] = f"{sum(valid)}/{len(valid)}"
    elif result:
        stages["citations"] = False
        detail["citations_valid"] = "0/0"
    return finish(case, artifact, stages, detail, expected_route, declined)


def finish(case, artifact, stages, detail, expected_route, declined):
    correct = correct_overall(case, stages, expected_route)
    first_false = next((s for s in STAGES if stages[s] is False), None)
    # A correct answer from sources nobody listed is not a drop-out; keep where the
    # key-source trail ended as a diagnostic instead.
    dropped = None if correct and first_false in SOURCE_STAGES else first_false
    detail["trail_ended_at"] = next((s for s in SOURCE_STAGES if stages[s] is False), None)
    return {
        "id": case["id"],
        "case_type": case.get("case_type"),
        "expected_route": expected_route,
        "stages": stages,
        "dropped_at": dropped,
        "correct": correct,
        "cause": likely_cause(artifact) if dropped else None,
        "detail": detail,
        "elapsed_seconds": artifact.get("elapsed_seconds"),
        "usage": usage(artifact),
    }


def correct_overall(case, stages, expected_route):
    """Team rule: partial or failed runs count as wrong; a decline case is right only if declined.

    None only when the case has no label yet; a run that dropped before the answer is False.
    """
    if expected_route == "decline":
        return stages["interpretation"] is True
    if not case.get("expected"):
        return None
    return stages["final_answer"] is True


# ---------- a whole run ----------


def summarize(rows):
    n = len(rows)
    reached = {s: sum(r["stages"][s] is True for r in rows) for s in STAGES}
    drops = Counter(r["dropped_at"] for r in rows if r["dropped_at"])
    causes = {
        stage: Counter(
            f"{r['cause']['stop_reason']} / {r['cause']['last_rejection']}"
            for r in rows if r["dropped_at"] == stage
        ).most_common(3)
        for stage in drops
    }
    research = [r for r in rows if r["expected_route"] == "research" and r["correct"] is not None]
    completed = [r for r in research if r["detail"].get("completed")]
    declines = [r for r in rows if r["expected_route"] == "decline"]
    return {
        "cases": n,
        "passed_stage": reached,
        "dropped_at": dict(drops),
        "top_causes": causes,
        "label_accuracy_completed": rate(sum(bool(r["correct"]) for r in completed), len(completed)),
        "label_accuracy_overall": rate(sum(bool(r["correct"]) for r in research), len(research)),
        "declined_correctly": rate(sum(bool(r["correct"]) for r in declines), len(declines)),
    }


def rate(k, n):
    """k/n with a 95% Wilson interval, so small samples show their noise."""
    if n == 0:
        return {"k": 0, "n": 0, "rate": None, "ci95": None}
    z = 1.96
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return {"k": k, "n": n, "rate": round(p, 3), "ci95": [round(max(0, centre - half), 3), round(min(1, centre + half), 3)]}


def find_artifact(run_dir, case_id):
    for path in (run_dir / f"{case_id}.json", run_dir / case_id / f"{case_id}.json"):
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8")), path
    return {}, None


def grade_run(run_dir, cases, keys_dir=None):
    rows = []
    for case in cases:
        artifact, path = find_artifact(run_dir, case["id"])
        keys = {}
        if keys_dir and (keys_dir / f"{case['id']}.json").is_file():
            keys = json.loads((keys_dir / f"{case['id']}.json").read_text(encoding="utf-8"))
        row = grade_case(case, artifact, keys)
        row["artifact"] = str(path.relative_to(run_dir)) if path else None
        rows.append(row)
    return {"summary": summarize(rows), "cases": rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--keys", type=Path, help="directory of stage-key sidecars")
    args = parser.parse_args(argv)
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    graded = grade_run(args.run_dir, cases, args.keys)
    out = args.run_dir / "stage-results.json"
    out.write_text(json.dumps(graded, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = graded["summary"]
    print(" > ".join(f"{st} {s['passed_stage'][st]}" for st in STAGES), f"(of {s['cases']})")
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
