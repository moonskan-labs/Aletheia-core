"""Check every cited passage of a finished batch, then write the batch report.

Code checks need no network. The judge model runs only here, never in the product.
"""

import argparse
import asyncio
import json
from pathlib import Path

from evaluate_research import MeteredTransport

from aletheia.config import ConfigurationError, ProviderSettings
from aletheia.evaluation import BatchClaim, write_json
from aletheia.providers.nebius import NebiusProvider
from aletheia.source_check import check_claim, report_csv, report_rows, report_summary


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def batch_claims(batch):
    return [BatchClaim.model_validate(c) for c in load(batch / "labels.json")]


async def check_batch(batch, claims, judge, parallel):
    (batch / "source_check").mkdir(exist_ok=True)
    limit = asyncio.Semaphore(parallel)

    async def one(claim):
        target = batch / "source_check" / f"{claim.id}.json"
        source = batch / "claims" / f"{claim.id}.json"
        if target.exists() or not source.exists():
            return
        async with limit:
            snapshots = load(batch / "snapshots" / f"{claim.id}.json")
            write_json(target, await check_claim(claim, load(source), snapshots, judge))
            print(json.dumps({"checked": claim.id}), flush=True)

    await asyncio.gather(*(one(c) for c in claims))


def write_report(batch, claims):
    artifacts = {p.stem: load(p) for p in (batch / "claims").glob("*.json")}
    checks = {p.stem: load(p) for p in (batch / "source_check").glob("*.json")}
    rows = report_rows(claims, artifacts, checks)
    manifest = load(batch / "manifest.json")
    (batch / "report.csv").write_text(report_csv(rows), encoding="utf-8")
    summary = report_summary(rows, manifest, len(claims))
    (batch / "report.md").write_text(summary, encoding="utf-8")
    return summary


async def run(args):
    claims = batch_claims(args.batch)
    if args.report_only:
        return
    if args.judge_model is None:
        await check_batch(args.batch, claims, None, args.parallel)
        return
    manifest = load(args.batch / "manifest.json")
    if args.judge_model == manifest["model"]:
        raise ConfigurationError("The judge must differ from the model under test.")
    settings = ProviderSettings.from_environment(dotenv_path=args.dotenv)
    settings = ProviderSettings.model_validate(
        {**settings.model_dump(), "nebius_model": args.judge_model, "nebius_thinking": "default"}
    )
    async with NebiusProvider(settings, transport=MeteredTransport("nebius", [])) as judge:
        await check_batch(args.batch, claims, judge, args.parallel)
    manifest["judge_model"] = args.judge_model
    write_json(args.batch / "manifest.json", manifest)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True, help="batch output directory")
    parser.add_argument("--judge-model", help="stronger model; omit for code checks only")
    parser.add_argument("--dotenv", type=Path)
    parser.add_argument("--parallel", type=int, default=6)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        asyncio.run(run(args))
    except ConfigurationError as exc:
        print(f"Source check stopped: {exc}")
        return 2
    print(write_report(args.batch, batch_claims(args.batch)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
