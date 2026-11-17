"""Opt-in stage diagnostic on frozen excerpts; not a factual-accuracy evaluation."""

import argparse
import asyncio
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from evaluate_research import MeteredTransport
from rerun_phase_one_pilot import HANDOFF, load_pilot

from aletheia.budgets import RunBudget
from aletheia.claims import interpret
from aletheia.config import ProviderSettings
from aletheia.evaluation import write_json
from aletheia.evidence import snapshot
from aletheia.providers.errors import ErrorCode, ProviderError
from aletheia.providers.nebius import NebiusProvider
from aletheia.tasks import InvalidTask, Tasks
from aletheia.verdicts import finding
from aletheia.verification import assess

CASE_IDS = ("b0001", "b0002", "b0004", "b0006", "b0023", "b0028")
CONTROLS = (
    ("route-causal-1", "Daily use of Treatment Q extends lifespan in healthy adults."),
    (
        "route-record-1",
        "The 2020 Trial Q report states that its treatment group lived longer "
        "than its control group.",
    ),
    ("route-causal-2", "Policy Q reduced unemployment in Region R compared with Region S."),
    ("route-record-2", "The 2020 Region R census records an unemployment rate of 7 percent."),
)
CAP = 40


class CappedTransport(MeteredTransport):
    async def handle_async_request(self, request):
        if len(self.attempts) >= CAP:
            raise ProviderError("nebius", ErrorCode.BUDGET)
        return await super().handle_async_request(request)


def frozen_source(case_id):
    """One source per case, preserving its saved quote text and provenance."""
    saved = json.loads((HANDOFF / "rerun/cases" / f"{case_id}.json").read_text())
    evidence = saved["evidence"]["evidence"]
    if not evidence:
        return None
    selected = next(
        (
            e
            for e in evidence
            if case_id == "b0002" and any("58 million km" in q["text"] for q in e["excerpts"])
        ),
        evidence[0],
    )
    source_id = selected["assessment"]["citation"]["snapshot_id"]
    metadata = next(s for s in saved["evidence"]["sources"] if s["id"] == source_id)
    quotes = {}
    for item in evidence:
        if item["assessment"]["citation"]["snapshot_id"] == source_id:
            for q in item["excerpts"]:
                quotes[(q["start"], q["end"], q["text"])] = q["text"]
    src = snapshot(
        url=metadata["url"],
        title=metadata["title"],
        published_date=metadata["published_date"],
        retrieved_at=datetime.fromisoformat(metadata["retrieved_at"].replace("Z", "+00:00")),
        text="\n".join(quotes[k] for k in sorted(quotes)),
    )
    src.limitations.append(
        "Stage diagnostic uses frozen cited excerpts, not a complete page or fresh retrieval."
    )
    return src


def cases():
    pilot, baseline = load_pilot()
    chosen = [(c.id, c.claim) for c in pilot if c.id in CASE_IDS]
    return chosen + list(CONTROLS), baseline


async def execute(output, settings):
    output.mkdir(parents=True, exist_ok=False)
    attempts, rows = [], []
    selected, _ = cases()
    revision = await asyncio.to_thread(
        subprocess.check_output, ["git", "rev-parse", "HEAD"], text=True
    )
    dirty = await asyncio.to_thread(
        subprocess.check_output, ["git", "status", "--porcelain"], text=True
    )
    manifest = {
        "stage_diagnostic_only": True,
        "case_ids": [id for id, _ in selected],
        "max_model_network_attempts": CAP,
        "tavily_calls": 0,
        "config": settings.model_dump(exclude={"nebius_api_key", "tavily_api_key"}),
        "revision": revision.strip(),
        "working_tree_dirty": bool(dirty.strip()),
        "started_at": datetime.now(UTC).isoformat(),
    }
    write_json(output / "manifest.json", manifest)
    async with NebiusProvider(settings, transport=CappedTransport("nebius", attempts)) as model:
        for id, claim in selected:
            row = {"id": id, "claim": claim, "status": "started", "events": []}
            rows.append(row)
            budget = RunBudget()
            budget.escalate()

            async def emit(event, payload, *, row=row):
                row["events"].append({"type": event, "payload": payload})

            tasks = Tasks(model, budget, emit)
            try:
                plan = await interpret(tasks, SimpleNamespace(claim=claim, context={}))
                row["interpretation"] = plan.model_dump()
                row["status"] = "interpreted"
                src = frozen_source(id) if id in CASE_IDS else None
                if plan.analysis.supported and not plan.questions and src is not None:
                    checked, gap = await assess(tasks, plan.assertions[0], src)
                    row.update(
                        status="assessed",
                        source=src.model_dump(mode="json"),
                        evidence=[e.model_dump() for e in checked],
                        gap=gap,
                        provisional_finding=finding(plan.assertions[0], "deep", checked, [src])[
                            0
                        ].model_dump(),
                    )
            except (ProviderError, InvalidTask) as exc:
                row["status"] = (
                    "invalid_task_output" if isinstance(exc, InvalidTask) else exc.code.value
                )
            finally:
                row["usage"] = tasks.tokens
                write_json(output / "results.json", rows)
                print(
                    json.dumps(
                        {"id": id, "status": row["status"], "model_attempts_total": len(attempts)}
                    ),
                    flush=True,
                )
            if len(attempts) >= CAP or any(
                n["status_code"] in {400, 401, 402, 403, 404, 422, 432, 433} for n in attempts
            ):
                break
    manifest.update(
        finished_at=datetime.now(UTC).isoformat(), network_attempts=attempts, recorded=len(rows)
    )
    write_json(output / "manifest.json", manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--dotenv", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    selected, baseline = cases()
    # Validate all frozen sources without making provider calls or loading credentials.
    for id in CASE_IDS:
        frozen_source(id)
    if not args.live:
        print(
            json.dumps(
                {
                    "cases": len(selected),
                    "maximum_model_attempts": CAP,
                    "tavily_calls": 0,
                    "live": False,
                }
            )
        )
        return
    if args.output is None:
        parser.error("A fresh --output directory is required.")
    loaded = ProviderSettings.from_environment(dotenv_path=args.dotenv)
    settings = ProviderSettings.model_validate({**loaded.model_dump(), **baseline["config"]})
    if not settings.nebius_api_key:
        raise SystemExit("Model credentials are incomplete; no call made.")
    asyncio.run(execute(args.output, settings))


if __name__ == "__main__":
    main()
