"""Score saved batch runs against the labels of any claims CSV, offline.

Uses the same decision rules and report as score_trusted.py; only the label rows differ.
An `almost` label counts as false, as in Phase 1 scoring.
"""

import argparse
import sys
from pathlib import Path

from score_trusted import report, score_run

from aletheia.evaluation import load_claims_csv


def sheet_rows(path):
    rows = []
    for claim in load_claims_csv(path):
        outcome, verdict, _ = claim.expected
        label = verdict if outcome == "decided" else "cannot_settle"
        rows.append({"id": claim.id, "verdict": label})
    return rows


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("claims_csv", type=Path)
    parser.add_argument("runs", type=Path, nargs="+")
    args = parser.parse_args(argv)
    try:
        rows = sheet_rows(args.claims_csv)
        text = report([score_run(folder, rows) for folder in args.runs])
        trusted_note = (
            "Tokens cover only the included trusted claims; "
            "excluded historical claims are ignored. "
        )
        text = text.replace("Tokens (trusted subset)", "Tokens").replace(
            trusted_note, "Tokens cover the claims in the sheet. "
        )
        print(text, end="")
        return 0
    except (ValueError, KeyError, OSError):
        print("Sheet scoring stopped: check the claims CSV and run folders.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
