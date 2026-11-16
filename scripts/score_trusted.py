"""Score saved batch/baseline runs against the fixed 77 trusted tuning labels, offline."""

import argparse
import json
from pathlib import Path

from aletheia.source_check import interval
from aletheia.trusted_evaluation import CLAIMS, csv_rows, trusted_rows


def decision(artifact):
    if artifact.get("kind") == "baseline":
        value = artifact.get("verdict")
        return value if value in {"true", "false", "cannot_settle"} else "no answer"
    result = (artifact.get("investigation") or {}).get("result") or {}
    if result.get("outcome") == "unable_to_decide":
        return "cannot_settle"
    if result.get("outcome") == "decided" and result.get("verdict") in {"true", "false"}:
        return result["verdict"]
    return "no answer"


def token_count(artifact):
    if artifact.get("kind") == "baseline":
        value = (artifact.get("token_usage") or {}).get("total_tokens")
        return value or 0, value is None
    # task_finished also accounts for failed calls when no final result was saved.
    events = [e for e in artifact.get("events", []) if e["type"] == "task_finished"]
    if events:
        values = [e["payload"].get("total_tokens") for e in events]
        known = [int(v) for v in values if str(v).isdigit()]
        return sum(known), len(known) != len(values)
    value = (
        ((artifact.get("investigation") or {}).get("result") or {}).get("token_usage") or {}
    ).get("total_tokens")
    return value or 0, value is None


def score_run(folder, rows):
    if not folder.is_dir():
        raise ValueError("Run folder does not exist")
    manifest_file = folder / "manifest.json"
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        if manifest.get("split") == "heldout":
            raise ValueError("Heldout scoring is forbidden")
        heldout = {r["id"] for r in csv_rows(CLAIMS) if r["split"] == "heldout"}
        if heldout.intersection(manifest.get("claim_ids", manifest.get("case_ids", []))):
            raise ValueError("Run contains heldout claims")
    answered = correct = matches = tokens = unknown = downgraded = 0
    wrong, decisions = [], {}
    # Only open included IDs. Historical runs also contain excluded claims, which
    # cannot affect the denominator, errors or token totals of this trusted subset.
    for row in rows:
        path = folder / "claims" / f"{row['id']}.json"
        if not path.exists():
            path = folder / f"{row['id']}.json"
        artifact = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        value = decision(artifact)
        decisions[row["id"]] = value
        answered += value in {"true", "false"}
        correct += value in {"true", "false"} and value == row["verdict"]
        matches += value == row["verdict"]
        if value != "no answer" and value != row["verdict"]:
            wrong.append(f"{row['id']} ({value}; expected {row['verdict']})")
        usage, incomplete = token_count(artifact)
        tokens += usage
        unknown += bool(artifact) and incomplete
        downgraded += bool(artifact.get("downgraded"))
    return {
        "run": folder.name,
        "total": len(rows),
        "answered": answered,
        "correct": correct,
        "matches": matches,
        "interval": interval(matches, len(rows)),
        "tokens": tokens,
        "unknown_tokens": unknown,
        "downgraded": downgraded,
        "wrong": wrong,
        "decisions": decisions,
    }


def report(scores):
    lines = [
        "| Run | True/false answers | Right among those | Total matches | 95% interval | "
        "Tokens (trusted subset) | Quote downgrades |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for score in scores:
        low, high = score["interval"]
        tokens = str(score["tokens"])
        if score["unknown_tokens"]:
            tokens += f" + unknown for {score['unknown_tokens']} claims"
        lines.append(
            f"| {score['run']} | {score['answered']}/{score['total']} | "
            f"{score['correct']}/{score['answered']} | {score['matches']}/{score['total']} | "
            f"{low}–{high}% | {tokens} | {score['downgraded']} |"
        )
    lines.extend(
        [
            "",
            "No result is 'no answer', never cannot_settle. Total matches include cannot_settle. "
            "Intervals use the existing Wilson 95% function; they do not measure run-to-run noise.",
            "Tokens cover only the included trusted claims; excluded historical claims "
            "are ignored. "
            "Missing usage is reported as unknown rather than zero.",
            "",
        ]
    )
    for score in scores:
        lines.append(f"Wrong answers — {score['run']}: " + (", ".join(score["wrong"]) or "none"))
        unanswered = [k for k, v in score["decisions"].items() if v == "no answer"]
        lines.append("No answer: " + (", ".join(unanswered) or "none"))
    if len(scores) > 1:
        lines.extend(["", "Pairwise differences (including cannot_settle and no answer):"])
        for i, left in enumerate(scores):
            for right in scores[i + 1 :]:
                changed = sum(
                    left["decisions"][k] != right["decisions"][k] for k in left["decisions"]
                )
                lines.append(
                    f"- {left['run']} / {right['run']}: {changed}/{left['total']} answers differ; "
                    f"total-match gap {abs(left['matches'] - right['matches'])}/{left['total']}."
                )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, help="new Markdown file")
    parser.add_argument("--split", choices=["tuning"], default="tuning")
    args = parser.parse_args(argv)
    try:
        rows = trusted_rows()
        text = report([score_run(folder, rows) for folder in args.runs])
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(text)
        print(text, end="")
        return 0
    except (ValueError, KeyError, OSError):
        print("Trusted scoring stopped: check tuning run folders and choose a new output file.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
