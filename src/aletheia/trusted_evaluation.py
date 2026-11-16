"""Shared, offline inputs for the fixed 77-claim tuning evaluation.

Trusted annotations are used for selection/scoring only. Prompt builders explicitly
select claim text and saved-page fields; they never serialize annotation records.
"""

import csv
import gzip
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import httpx
from pydantic import SecretStr

from aletheia.evaluation import load_claims_csv
from aletheia.passages import terms
from aletheia.providers.tavily import TavilyProvider

ROOT = Path(__file__).resolve().parents[2]
TRUSTED = ROOT / "evals/claims/trusted-tuning-20261116.csv"
CLAIMS = ROOT / "evals/claims/claims-20261115.csv"
GROUND_TRUTH = ROOT / "evals/claims/ground-truth-20261116.csv"
EVIDENCE = ROOT / "evals/evidence"


def csv_rows(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def trusted_rows():
    rows = [r for r in csv_rows(TRUSTED) if r["included"] == "yes"]
    if len(rows) != 77 or len({r["id"] for r in rows}) != 77:
        raise ValueError("Expected exactly 77 distinct included tuning claims")
    if any(r["verdict"] not in {"true", "false", "cannot_settle"} for r in rows):
        raise ValueError("Included claims must have settled reference labels")
    return rows


def trusted_claims(*, ids=None, split="tuning"):
    if split not in (None, "tuning"):
        raise ValueError("Heldout evaluation is forbidden")
    allowed = {r["id"] for r in trusted_rows()}
    selected = set(ids) if ids is not None else allowed
    if not selected or not selected <= allowed:
        raise ValueError("Only included trusted tuning IDs are allowed")
    return load_claims_csv(CLAIMS, split="tuning", ids=sorted(selected))


def validate_claims(claims):
    canonical = {c.id: c for c in trusted_claims()}
    if not claims or len({c.id for c in claims}) != len(claims):
        raise ValueError("Expected distinct trusted tuning claims")
    for claim in claims:
        if (
            claim.id not in canonical
            or claim.split != "tuning"
            or claim.claim != canonical[claim.id].claim
        ):
            raise ValueError("Only original included trusted tuning claims are allowed")


def load_pages(directory, claim_id):
    if claim_id not in {r["id"] for r in trusted_rows()}:
        raise ValueError("Only included trusted tuning IDs are allowed")
    path = directory / "pages" / f"{claim_id}.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        pages = json.load(handle)
    if not isinstance(pages, list):
        raise ValueError("Expected a saved page list")
    for page in pages:
        if not all(isinstance(page.get(k), str) for k in ("url", "title", "original_text")):
            raise ValueError("Invalid saved page")
    return pages


def collapse(text):
    return " ".join(text.split())


def _number(text):
    value = float(text.replace(",", "").strip())
    if value != value or value in (float("inf"), float("-inf")):
        raise ValueError("Not a finite number")
    return value


def compare_values(kind, first, second, first_unit, second_unit, relation):
    """Compare two separately quoted values in code; numbers and dates only.

    Returns "true" or "false" for the stated relation, or "cannot_settle" when a value
    is missing or unparseable or the units differ. A later date is the greater one.
    """
    if first is None or second is None:
        return "cannot_settle"
    if collapse(first_unit).casefold() != collapse(second_unit).casefold():
        return "cannot_settle"
    try:
        if kind == "date":
            left, right = date.fromisoformat(first.strip()), date.fromisoformat(second.strip())
        else:
            left, right = _number(first), _number(second)
    except ValueError:
        return "cannot_settle"
    holds = {
        "first_greater": left > right,
        "first_less": left < right,
        "equal": left == right,
    }[relation]
    return "true" if holds else "false"


def ranked_pages(query, pages):
    query_terms = terms(query)
    return sorted(
        pages,
        key=lambda page: -len(query_terms & terms(page["title"] + " " + page["original_text"])),
    )  # Stable ties retain archive order, including multiple versions of one URL.


class ReplayProvider(TavilyProvider):
    """Saved responses through an in-memory transport; no socket or Tavily key.

    Reuse the real adapter's validation, per-URL reservations, deadline checks,
    attempt records and truncation. The transport cannot perform network I/O.
    One lane calls set_pages only between completed investigations.
    """

    def __init__(self, settings):
        self.set_pages([])
        super().__init__(
            settings.model_copy(update={"tavily_api_key": SecretStr("offline-replay")}),
            transport=httpx.MockTransport(self._respond),
        )

    def set_pages(self, pages):
        # A URL can have multiple saved revisions. Use its first archived revision
        # consistently for both search and extraction, never a query-dependent one.
        self.pages = []
        self.by_url = {}
        for page in pages:
            aliases = {page["url"], page.get("canonical_url") or page["url"]}
            if any(url in self.by_url for url in aliases):
                continue
            self.pages.append(page)
            for url in aliases:
                self.by_url[url] = page

    def _respond(self, request):
        payload = json.loads(request.content)
        if request.url.path == "/search":
            query = payload["query"]
            query_terms = terms(query)
            hits = []
            for page in ranked_pages(query, self.pages)[: payload["max_results"]]:
                overlap = len(query_terms & terms(page["title"] + " " + page["original_text"]))
                hits.append(
                    {
                        "url": page["url"],
                        "title": page["title"],
                        "content": page["original_text"][:6000],
                        "published_date": page.get("published_date"),
                        "score": overlap / max(1, len(query_terms)),
                    }
                )
            return httpx.Response(200, json={"results": hits})
        if request.url.path == "/extract":
            url = payload["urls"][0]
            page = self.by_url.get(url)
            return httpx.Response(
                200,
                json={
                    "results": [{"url": url, "raw_content": page["original_text"]}] if page else [],
                    "failed_results": [] if page else [{"url": url}],
                },
            )
        raise AssertionError("Unexpected replay operation")

    async def extract(self, urls, *, budget, depth="basic"):
        result = await super().extract(urls, budget=budget, depth=depth)
        pages = []
        for outcome in result.pages:
            saved = self.by_url.get(outcome.url)
            pages.append(
                replace(
                    outcome,
                    error="not_available"
                    if outcome.error == "extraction_failed"
                    else outcome.error,
                    limitations=tuple(
                        dict.fromkeys([*outcome.limitations, *(saved or {}).get("limitations", [])])
                    ),
                )
            )
        return replace(result, pages=tuple(pages))
