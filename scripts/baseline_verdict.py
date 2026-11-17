"""One model call per included trusted tuning claim, using only saved pages."""

import argparse
import asyncio
import json
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from evaluate_research import git_state

from aletheia.budgets import CallBudget
from aletheia.config import ConfigurationError, ProviderSettings
from aletheia.evaluation import write_json
from aletheia.evidence import snapshot
from aletheia.one_call import (  # noqa: F401
    INSTRUCTIONS,
    Answer,
    Quote,
    offer_pages,
    validate_answer,
)
from aletheia.providers.errors import ProviderError
from aletheia.providers.nebius import NebiusProvider
from aletheia.trusted_evaluation import (
    EVIDENCE,
    load_pages,
    ranked_pages,
    trusted_claims,
    validate_claims,
)


def prompt_pages(claim_text, saved_pages):
    sources = [
        snapshot(
            url=page["url"],
            title=page["title"],
            published_date=page.get("published_date"),
            retrieved_at=datetime.fromisoformat(page["retrieved_at"]),
            text=page["original_text"],
        )
        for page in saved_pages
    ]
    return offer_pages(claim_text, sources)[1]


async def evaluate_claim(claim, pages, model, deadline_seconds):
    offered = prompt_pages(claim.claim, pages)
    budget = CallBudget(1, 0, 0, time.monotonic() + deadline_seconds)
    artifact = {"id": claim.id, "kind": "baseline", "pages": offered}
    started = time.monotonic()
    try:
        response = await model.generate(
            instructions=INSTRUCTIONS,
            input_text=json.dumps({"claim": claim.claim, "pages": offered}, ensure_ascii=False),
            response_type=Answer,
            budget=budget,
        )
        originals = [p["original_text"] for p in ranked_pages(claim.claim, pages)[:6]]
        artifact.update(validate_answer(response.value, offered, originals))
        artifact["token_usage"] = response.usage.model_dump() if response.usage else None
    except ProviderError as exc:
        artifact.update(runner_error=exc.code.value, token_usage=exc.token_usage)
    except Exception:
        artifact.update(runner_error="baseline_failed", token_usage=None)
    finally:
        artifact["elapsed_seconds"] = round(time.monotonic() - started, 3)
        artifact["budget_attempts"] = [asdict(a) for a in budget.attempts]
    return artifact


async def run(args, claims, *, settings=None, model_factory=NebiusProvider):
    validate_claims(claims)
    if not 1 <= args.parallel <= 12:
        raise ValueError("Parallelism must be 1 to 12")
    # Load all inputs before creating clients or making any paid call.
    pages = {c.id: load_pages(EVIDENCE, c.id) for c in claims}
    settings = settings or ProviderSettings.from_environment()
    settings = ProviderSettings.model_validate(
        {**settings.model_dump(), "nebius_model": args.model, "max_retries": 0}
    )
    if not settings.nebius_api_key:
        raise ConfigurationError("NEBIUS_API_KEY is required in the environment")
    settings.validate_model_controls()
    revision, dirty = git_state()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "claims").mkdir()
    manifest = {
        "kind": "baseline",
        "model": settings.nebius_model,
        "revision": revision,
        "working_tree_dirty": dirty,
        "started_at": datetime.now(UTC).isoformat(),
        "claim_ids": [c.id for c in claims],
        "split": "tuning",
        "parallel": args.parallel,
        "evidence_directory": str(EVIDENCE.resolve()),
        "nebius_thinking": settings.nebius_thinking,
        "response_format": settings.nebius_response_format,
        "max_output_tokens": settings.max_output_tokens,
        "provider_timeout_seconds": settings.timeout_seconds,
        "max_retries": 0,
        "live": True,
    }
    write_json(args.output / "manifest.json", manifest)
    semaphore = asyncio.Semaphore(args.parallel)
    artifacts = []

    async def one(claim):
        async with semaphore:
            async with model_factory(settings) as model:
                artifact = await evaluate_claim(
                    claim, pages[claim.id], model, settings.timeout_seconds
                )
            write_json(args.output / "claims" / f"{claim.id}.json", artifact)
            artifacts.append(artifact)

    try:
        # TaskGroup cancels remaining tasks before final accounting on an I/O failure.
        async with asyncio.TaskGroup() as group:
            for claim in claims:
                group.create_task(one(claim))
    finally:
        manifest.update(
            finished_at=datetime.now(UTC).isoformat(),
            recorded=len(artifacts),
            not_run=len(claims) - len(artifacts),
            failed=sum("runner_error" in a for a in artifacts),
            downgraded=sum(a.get("downgraded", False) for a in artifacts),
            token_totals={
                key: sum((a.get("token_usage") or {}).get(key, 0) for a in artifacts)
                for key in ("prompt_tokens", "completion_tokens", "total_tokens")
            },
            token_usage_missing=sum(a.get("token_usage") is None for a in artifacts),
        )
        write_json(args.output / "manifest.json", manifest)
    return len(artifacts) == len(claims) and not manifest["failed"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--parallel", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True, help="must be a new folder")
    parser.add_argument("--ids", help="comma-separated included tuning IDs")
    parser.add_argument("--split", choices=["tuning"], default="tuning")
    args = parser.parse_args(argv)
    try:
        claims = trusted_claims(ids=args.ids.split(",") if args.ids else None, split=args.split)
        return 0 if asyncio.run(run(args, claims)) else 1
    except (ValueError, OSError, ConfigurationError, ProviderError, ExceptionGroup):
        print("Baseline stopped: check inputs, new output folder and environment settings.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
