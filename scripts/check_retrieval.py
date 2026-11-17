"""Offline URL, site and literal-quote checks for the 77 included tuning claims."""

import argparse
import csv
from pathlib import Path
from urllib.parse import urlsplit

from aletheia.trusted_evaluation import (
    EVIDENCE,
    GROUND_TRUTH,
    collapse,
    csv_rows,
    load_pages,
    trusted_rows,
)

NOTICE = (
    '"Not found" by these checks does not prove the evidence is absent from the pages. '
    "These are URL and literal-text checks, not semantic judgements."
)


def site(url):
    host = (urlsplit(url).hostname or "").lower()
    return host.removeprefix("www.")


def page_key(url):
    parts = urlsplit(url)
    return site(url), parts.port, parts.path.rstrip("/"), parts.query


def check(rows, references, evidence):
    results = []
    for row in rows:
        pages = load_pages(evidence, row["id"])
        reference = references[row["id"]]
        urls = [p[k] for p in pages for k in ("url", "canonical_url") if p.get(k)]
        quote = collapse(reference["quote"])
        results.append(
            {
                "id": row["id"],
                "same_page": bool(row["source_url"])
                and any(page_key(u) == page_key(row["source_url"]) for u in urls),
                "same_site": bool(row["source_url"])
                and any(site(u) == site(row["source_url"]) for u in urls),
                "quote_found": bool(quote)
                and any(quote in collapse(p["original_text"]) for p in pages),
                "quote_available": bool(quote),
            }
        )
    return results


def summary(rows):
    lines = [f"Retrieval checks: {len(rows)} included tuning claims."]
    for key, label in (
        ("same_page", "Same trusted source page"),
        ("same_site", "Same trusted source site"),
        ("quote_found", "Trusted primary quote found verbatim"),
        ("quote_available", "Trusted primary quote supplied"),
    ):
        lines.append(f"{label}: {sum(r[key] for r in rows)}/{len(rows)}")
    lines.extend(
        [
            "",
            "Page identity ignores scheme, www., fragment and trailing slash; query strings "
            "are retained. Site means the same hostname after removing www. (not all subdomains).",
            "Quote matching uses the primary quote column, collapses whitespace only, and is "
            "case/punctuation sensitive; it does not remove Markdown or search for quote_2.",
            NOTICE,
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new output folder")
    parser.add_argument("--split", choices=["tuning"], default="tuning")
    args = parser.parse_args(argv)
    try:
        rows = trusted_rows()
        references = {r["id"]: r for r in csv_rows(GROUND_TRUTH)}
        results = check(rows, references, EVIDENCE)
        args.output.mkdir(parents=True, exist_ok=False)
        with (args.output / "retrieval.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results)
        report = summary(results)
        (args.output / "summary.txt").write_text(report, encoding="utf-8")
        print(report, end="")
        return 0
    except (ValueError, KeyError, OSError):
        print("Retrieval check stopped: check saved inputs and choose a new output folder.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
