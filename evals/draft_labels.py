"""Draft labels and stage keys with Claude Fable 5.2, for humans to check. Costs money.

    python evals/draft_labels.py --ids b0001,n0001 --out <run_dir>

Each claim from evals/cases/v1-inputs.json gets one Fable 5.2 request with web search and
web fetch. Fable writes a draft record in the evals/ format plus a stage-key sidecar
(accepted URLs and sites, decisive quotes, expected relation). A draft is never an answer
key: drafts go to <run_dir>/drafts/, outside labels/, so the validator can never count
Fable as a labeler. Chandra and Pari label blind and only then compare.

Per claim the run writes drafts/<id>.json, stage-keys/<id>.json, traces/<id>.json and one
row in results.jsonl (served model, usage, searches, validation, quote checks); attempts
that produced nothing usable go to errors.jsonl. Rerunning skips claims already drafted.

Reads ANTHROPIC_API_KEY from the environment and never prints it. No refusal fallback is
configured on purpose: a draft must come from the model it is attributed to, so a refusal
is recorded as an error rather than silently answered by another model.
"""

import argparse
import asyncio
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_stages import normalize_url, quote_found  # noqa: E402
from validate import SchemaChecker, load_schema, record_rules  # noqa: E402

EVALS = Path(__file__).resolve().parent
MODEL = "claude-fable-5-2"
LABELER = "fable-5-2"
PRICES = {  # USD per million tokens; searches per 1,000. Source: platform.claude.com pricing.
    MODEL: {"in": 8.0, "out": 40.0, "cache_write": 10.0, "cache_read": 0.20, "search_per_1k": 10.0}
}
RELATIONS = ("supports", "contradicts", "context")
MAX_CONTINUATIONS = 6  # pause_turn resumptions per request


def labeling_rules():
    """The decision rules exactly as the human labelers read them."""
    text = (EVALS / "README.md").read_text(encoding="utf-8")
    start, end = text.index("### The decision"), text.index("### Agreement rate")
    return text[start:end].strip()


SYSTEM = """You draft labels for an evaluation set used to test an automated fact-checking \
backend. Two people will label every claim blind and then compare with your draft; your \
draft helps them find what to recheck and never becomes the answer key on its own. So be \
accurate rather than agreeable, and say plainly when a claim is genuinely hard.

Research each claim on the web. Prefer primary and authoritative sources (the original \
record, the official publisher, a peer-reviewed paper, a recognised synthesis). Fetch each \
source you rely on with web_fetch, so that what you quote is copied from the page itself.

Labeling rules (the same rules the human labelers follow):

{rules}

Besides the record, write stage keys that let code check whether the backend found and used \
the evidence that settles the claim. For each key source:
- urls: the page you fetched, plus other exact URLs a run could reasonably read for the same \
evidence (the official PDF of a landing page, a canonical or mirror copy).
- sites: host names whose every page counts as this source (for example "unfccc.int"). Use [] \
when only the exact pages count, e.g. for a single article on a large general site.
- decisive_quotes: one or two short passages (one or two sentences, under 300 characters) \
copied verbatim from the fetched page, that settle the claim or the needed correction.
- expected_relation: "supports", "contradicts" or "context", from the claim's point of view.

Return your answer as the last thing in your reply: one ```json block holding exactly this \
object, and nothing after it:
{{"record": <the claim record>, "stage_keys": {{"key_sources": [<one entry per record \
key_source, same order>]}}, "notes_for_reviewers": "<what was hard, any reading you were \
unsure of, anything the humans should check first>"}}
"""


def user_prompt(case, today):
    hint = {
        "decline": "The team expects the backend to decline this claim as outside what it can "
        "check (causal or predictive); label it anyway, as the rules say.",
        "research": "",
    }[case.get("route_hint", "research")]
    record_shape = {
        "id": case["id"],
        "split": "tuning",
        "claim": case["claim"],
        "context": case.get("context", {}),
        "case_type": case["case_type"],
        "expected": "<decision>",
        "acceptable_alternatives": [],
        "expected_flags": [
            {"type": "misleading_comparison | narrow_scope", "dimension": "<one of the nine>",
             "rationale": "<why a correct run should raise it>"}
        ],
        "key_sources": [{"url": "https://...", "shows": "what this source establishes"}],
        "as_of": today,
        "labelers": [LABELER],
        "status": "draft",
        "reviewer_note": "<why this decision>",
    }
    return (
        f"Claim to label:\n\n{json.dumps(case['claim'], ensure_ascii=False)}\n\n"
        f"Context submitted with it: {json.dumps(case.get('context', {}), ensure_ascii=False)}\n"
        f"case_type (fixed by the team): {case['case_type']}\n{hint}\n\n"
        "Keep id, split, claim, context, case_type, as_of, labelers and status exactly as in "
        "this shape. expected_flags may be empty; key_sources has 1 to 3 entries:"
        f"\n```json\n{json.dumps(record_shape, indent=2, ensure_ascii=False)}\n```"
    ).replace("\n\n\n", "\n\n")


# ---------- reading responses ----------


def final_json(content):
    text = "".join(b.text for b in content if b.type == "text")
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, flags=re.S)
    if not blocks:
        raise ValueError("no ```json block in the final reply")
    return json.loads(blocks[-1])


def page_key(url):
    """Fetch results can come back with tracking queries (?s_cid=...); match on host + path."""
    return normalize_url(url).split("?", 1)[0]


def fetched_pages(messages):
    """URL -> page text for every document web_fetch returned; None for PDFs (not checked)."""
    pages = {}
    for message in messages:
        for block in message["content"] if isinstance(message["content"], list) else []:
            block = block if isinstance(block, dict) else block.model_dump()
            if block.get("type") != "web_fetch_tool_result":
                continue
            result = block.get("content") or {}
            source = (result.get("content") or {}).get("source") or {}
            if result.get("type") != "web_fetch_result":
                continue
            if source.get("type") == "text":
                pages[page_key(result.get("url"))] = source.get("data", "")
            else:
                pages.setdefault(page_key(result.get("url")), None)
    return pages


def check_draft(case, draft, pages):
    """Return (problems, quote_checks). Problems block the draft; quote checks are reported."""
    problems = []
    record = draft.get("record")
    keys = (draft.get("stage_keys") or {}).get("key_sources")
    if not isinstance(record, dict):
        return ["record: missing"], []
    checker = SchemaChecker(load_schema())
    problems += checker.check(record, checker.root, "record")
    problems += record_rules(record, in_claims_file=False)
    for field in ("id", "claim", "case_type", "split"):
        if record.get(field) != {"split": "tuning"}.get(field, case.get(field)):
            problems.append(f"record.{field}: changed from the input")
    if record.get("labelers") != [LABELER] or record.get("status") != "draft":
        problems.append("record: labelers must be [fable-5-2] and status draft")
    if not isinstance(keys, list) or len(keys) != len(record.get("key_sources") or []):
        problems.append("stage_keys.key_sources: one entry per record key source")
        keys = []
    checks = []
    for i, key in enumerate(keys):
        where = f"stage_keys.key_sources[{i}]"
        if not key.get("urls") or not key.get("decisive_quotes"):
            problems.append(f"{where}: needs urls and decisive_quotes")
        if key.get("expected_relation") not in RELATIONS:
            problems.append(f"{where}.expected_relation: one of {RELATIONS}")
        fetched = [pages[u] for u in map(page_key, key.get("urls", [])) if u in pages]
        texts = [t for t in fetched if t is not None]
        for quote in key.get("decisive_quotes", []):
            found = any(quote_found(quote, t) for t in texts)
            checks.append({
                "source": i,
                "quote": quote[:80],
                "page_fetched": bool(fetched),
                # None: only a PDF (binary) copy was fetched, so the quote could not be checked.
                "verbatim_on_fetched_page": True if found else (None if fetched and not texts else False),
            })
    return problems, checks


def cost_usd(usage, searches):
    p = PRICES[MODEL]
    return round(
        (
            usage["input_tokens"] * p["in"]
            + usage["output_tokens"] * p["out"]
            + usage["cache_creation_input_tokens"] * p["cache_write"]
            + usage["cache_read_input_tokens"] * p["cache_read"]
        ) / 1e6
        + searches * p["search_per_1k"] / 1000,
        4,
    )


# ---------- one claim ----------


async def draft_one(client, case, args, out):
    today = dt.date.today().isoformat()
    messages = [{"role": "user", "content": user_prompt(case, today)}]
    usage = dict.fromkeys(
        ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"), 0
    )
    searches = fetches = requests = 0
    started = time.monotonic()
    repaired = False

    async def request():
        nonlocal searches, fetches, requests
        for _ in range(MAX_CONTINUATIONS + 1):
            async with client.messages.stream(
                model=MODEL,
                max_tokens=64000,
                system=SYSTEM.format(rules=labeling_rules()),
                output_config={"effort": args.effort},
                cache_control={"type": "ephemeral"},  # reuses the context on repair/pause turns
                tools=[
                    {"type": "web_search_20260318", "name": "web_search", "max_uses": args.max_searches},
                    # Direct calls, so the fetched page text reaches the transcript for quote checks.
                    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": args.max_fetches,
                     "max_content_tokens": args.max_page_tokens, "allowed_callers": ["direct"]},
                ],
                messages=messages,
            ) as stream:
                response = await stream.get_final_message()
            requests += 1
            if response.model != MODEL:
                raise ServedModelMismatch(response.model)
            for key in usage:
                usage[key] += getattr(response.usage, key, 0) or 0
            stu = getattr(response.usage, "server_tool_use", None)
            searches += getattr(stu, "web_search_requests", 0) or 0
            fetches += getattr(stu, "web_fetch_requests", 0) or 0
            messages.append({"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in response.content]})
            if response.stop_reason != "pause_turn":
                return response
        raise RuntimeError("too many pause_turn continuations")

    response = await request()
    problems, checks, draft = [], [], None
    if response.stop_reason == "refusal":
        problems = [f"refusal: {getattr(response.stop_details, 'category', None)}"]
    elif response.stop_reason == "max_tokens":
        problems = ["truncated at max_tokens"]
    else:
        try:
            draft = final_json(response.content)
            problems, checks = check_draft(case, draft, fetched_pages(messages))
        except (ValueError, json.JSONDecodeError) as error:
            problems = [f"unparseable: {error}"]
        if problems and not problems[0].startswith(("refusal", "truncated")):
            # One repair turn, appended (earlier turns are never edited).
            repaired = True
            messages.append({"role": "user", "content": "Your JSON has these problems; reply with the "
                             "corrected ```json block only:\n- " + "\n- ".join(problems)})
            response = await request()
            try:
                draft = final_json(response.content)
                problems, checks = check_draft(case, draft, fetched_pages(messages))
            except (ValueError, json.JSONDecodeError) as error:
                problems = [f"unparseable after repair: {error}"]

    trace = [{"role": "system", "content": SYSTEM.format(rules=labeling_rules())}] + [
        trace_turn(m) for m in messages
    ]
    write(out / "traces" / f"{case['id']}.json", trace)
    write(out / "raw" / f"{case['id']}.json", messages)  # full blocks, for re-checking without paying
    row = {
        "prompt_id": case["id"],
        "tags": [case["case_type"], case.get("source", ""), case.get("route_hint", "research")],
        "model": response.model,
        "stop_reason": response.stop_reason,
        "status": "truncated" if response.stop_reason == "max_tokens" else "ok",
        "usage": usage,
        "web_searches": searches,
        "web_fetches": fetches,
        "requests": requests,
        "repaired": repaired,
        "latency_s": round(time.monotonic() - started, 1),
        "cost_usd": cost_usd(usage, searches),
        "problems": problems,
        "quote_checks": checks,
        "quotes_verified": f"{sum(c['verbatim_on_fetched_page'] is True for c in checks)}/{len(checks)}",
        "quotes_unchecked_pdf": sum(c["verbatim_on_fetched_page"] is None for c in checks),
    }
    if problems:
        append(out / "errors.jsonl", {**row, "failure_class": problems[0].split(":")[0]})
        return row
    write(out / "drafts" / f"{case['id']}.json", draft["record"])
    write(out / "stage-keys" / f"{case['id']}.json", {
        "id": case["id"],
        "expected_route": case.get("route_hint", "research"),
        "key_sources": draft["stage_keys"]["key_sources"],
        "drafted_by": LABELER,
        "status": "draft",
    })
    write(out / "notes" / f"{case['id']}.txt", draft.get("notes_for_reviewers", ""))
    append(out / "results.jsonl", row)
    return row


class ServedModelMismatch(Exception):
    pass


def trace_turn(message):
    if isinstance(message["content"], str):
        return {"role": message["role"], "content": message["content"]}
    parts = []
    for b in message["content"]:
        if b["type"] == "text":
            parts.append(b["text"])
        elif b["type"] == "server_tool_use":
            parts.append(f"[{b['name']}] {json.dumps(b.get('input'))}")
        elif b["type"].endswith("_tool_result"):
            content = b.get("content")
            if isinstance(content, list):
                parts.append("[results] " + ", ".join(r.get("url", "") for r in content if isinstance(r, dict)))
            elif isinstance(content, dict):
                parts.append(f"[result] {content.get('url') or content.get('error_code') or content.get('type')}")
    return {"role": message["role"], "content": "\n".join(parts)}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


def append(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------- the run ----------


async def run(args):
    import anthropic  # imported here so the offline checks and their tests need no SDK

    cases = {c["id"]: c for c in json.loads(args.cases.read_text(encoding="utf-8"))}
    ids = args.ids.split(",") if args.ids else list(cases)
    unknown = [i for i in ids if i not in cases]
    if unknown:
        raise SystemExit(f"unknown ids: {unknown}")
    todo = [i for i in ids if not (args.out / "drafts" / f"{i}.json").exists()]
    client = anthropic.AsyncAnthropic(max_retries=4, timeout=args.timeout_s)
    gate = asyncio.Semaphore(args.concurrency)
    run_started = time.monotonic()

    spent = [0.0]

    async def one(case_id):
        async with gate:
            if spent[0] >= args.budget_usd:
                row = {"prompt_id": case_id, "failure_class": "budget_stop"}
                print(json.dumps(row), flush=True)
                return row
            try:
                row = await asyncio.wait_for(draft_one(client, cases[case_id], args, args.out), args.timeout_s)
            except asyncio.TimeoutError:
                row = {"prompt_id": case_id, "failure_class": "timeout"}
                append(args.out / "errors.jsonl", row)
            except ServedModelMismatch as served:
                row = {"prompt_id": case_id, "failure_class": "served_model_mismatch", "model": str(served)}
                append(args.out / "errors.jsonl", row)
            except anthropic.APIStatusError as error:
                row = {"prompt_id": case_id, "failure_class": "api_error", "status": error.status_code,
                       "message": str(error.message)[:300]}
                append(args.out / "errors.jsonl", row)
            except anthropic.APIConnectionError:
                row = {"prompt_id": case_id, "failure_class": "connection_error"}
                append(args.out / "errors.jsonl", row)
            spent[0] += row.get("cost_usd", 0)
            print(json.dumps({k: row.get(k) for k in (
                "prompt_id", "failure_class", "problems", "cost_usd", "web_searches", "latency_s", "quotes_verified")}),
                flush=True)
            return row

    rows = await asyncio.gather(*(one(i) for i in todo))
    done = [r for r in rows if "cost_usd" in r]
    total = sum(r["cost_usd"] for r in done)
    print(json.dumps({
        "attempted": len(todo), "skipped_already_drafted": len(ids) - len(todo),
        "drafted": sum(not r.get("problems") for r in done), "errors": len(rows) - sum(not r.get("problems") for r in done),
        "cost_usd_measured": round(total, 3), "wall_clock_s": round(time.monotonic() - run_started, 1),
    }))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cases", type=Path, default=EVALS / "cases" / "v1-inputs.json")
    parser.add_argument("--ids", help="comma-separated claim ids; default all")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--effort", default="high", choices=("low", "medium", "high", "xhigh", "max"))
    parser.add_argument("--max-searches", type=int, default=8)
    parser.add_argument("--max-fetches", type=int, default=6)
    parser.add_argument("--max-page-tokens", type=int, default=25000, help="cap per fetched page")
    parser.add_argument("--budget-usd", type=float, required=True,
                        help="stop starting new claims once measured spend in this run reaches this")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--timeout-s", type=float, default=900.0, help="hard ceiling per claim")
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
