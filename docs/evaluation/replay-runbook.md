# Replay evaluation on saved pages

This project investigates factual claims. This procedure compares a one-call model
baseline with the full research pipeline while giving both the same saved evidence
archive. It measures only the **77 tuning claims marked `included=yes`** in
`evals/claims/trusted-tuning-20261116.csv`. The other three tuning claims and every
heldout claim are excluded. These tools reject heldout requests. Never edit the
inclusion list, claim text, trusted labels or saved pages to improve a result.

The tools have offline tests; passing those tests does not establish answer accuracy.
The retrieval and scoring commands below only inspect saved files. The baseline and
three replay commands make paid model calls and are the evaluation itself. No
source-check judge is part of this procedure.

## Prerequisites

Work from the repository root on the revision containing these tools. Install `uv`
and Python 3.12 or later. Have `NEBIUS_API_KEY` already set in the environment and
network access to `api.tokenfactory.nebius.com`. No Tavily key or access to search
services or source websites is needed. Do not put keys in commands, artifacts or Git.
These commands do not read a dotenv file.

Install the project and its development dependencies:

```sh
uv sync
```

Use exactly `Qwen/Qwen3-235B-A22B-Instruct-2507` with
`ALETHEIA_NEBIUS_THINKING=default`. Set a date prefix once; for example, replace
`YYYYMMDD` below with `20261117`. All output names must be new. Keep the same terminal
open so these two variables remain set:

```sh
export RUN_DATE=YYYYMMDD
export ALETHEIA_NEBIUS_THINKING=default
```

Check that `evals/evidence/pages/`, the trusted tuning CSV, and
`evals/claims/ground-truth-20261116.csv` exist. The two historical folders
`evals/runs/20261116-tuning-qwen235/` and
`evals/runs/20261116-tuning-decision-gate/` must also be present.

## Commands, in order

### 1. Retrieval check

```sh
uv run python scripts/check_retrieval.py --output "evals/runs/${RUN_DATE}-retrieval-check/"
```

Produces `retrieval.csv` with one row per included claim, plus `summary.txt` with
counts for the same trusted page, same hostname and exact primary trusted quote.
Typically seconds. Quote matching collapses whitespace only, so Markdown and
punctuation differences can prevent a match. **“Not found” does not prove the evidence
is absent from the pages.** This is not a model-based relevance assessment.

### 2. Baseline, once

```sh
uv run python scripts/baseline_verdict.py --model Qwen/Qwen3-235B-A22B-Instruct-2507 --parallel 6 --output "evals/runs/${RUN_DATE}-baseline-qwen235/"
```

Makes one model attempt per claim, with no retries, using at most six saved pages and
about 6,000 selected characters per page. Produces `claims/<id>.json` with the offered
passages, original answer, valid/invalid quotes, final verdict and usage, plus a
`manifest.json` with model, revision, settings, totals and downgrade count. A true or
false answer without a valid exact quote becomes `cannot_settle`; technical failures
are kept as no answer. Allow roughly 1–10 minutes at six concurrent claims; this is a
planning estimate, not a measured runtime for this new tool.

### 3. Pipeline replay, three separate runs

```sh
uv run python scripts/evaluate_research.py --replay-evidence evals/evidence --split tuning --live --model Qwen/Qwen3-235B-A22B-Instruct-2507 --parallel 6 --output "evals/runs/${RUN_DATE}-replay-qwen235-a"
```

```sh
uv run python scripts/evaluate_research.py --replay-evidence evals/evidence --split tuning --live --model Qwen/Qwen3-235B-A22B-Instruct-2507 --parallel 6 --output "evals/runs/${RUN_DATE}-replay-qwen235-b"
```

```sh
uv run python scripts/evaluate_research.py --replay-evidence evals/evidence --split tuning --live --model Qwen/Qwen3-235B-A22B-Instruct-2507 --parallel 6 --output "evals/runs/${RUN_DATE}-replay-qwen235-c"
```

Each produces a manifest recording replay mode and the evidence directory, per-claim
results/traces in `claims/`, selected snapshots in `snapshots/`, `scores.json`, labels
for reporting, and local databases under `db/`. The original batch `scores.json` uses
the historical dataset labels; use **the trusted scorer below** for this comparison.
Labels and reference annotations are not model inputs. Search queries rank only that
claim's saved pages by word overlap. An unsaved URL returns `not_available`. When a
URL has multiple archived revisions, replay consistently uses the first archived
revision; search and extraction use the same revision. Search and extraction consume
the existing call budgets even though no search network request occurs. All network
requests go to the model.

Allow roughly 10–40 minutes per replay run, depending on model latency and follow-up
steps. This is a planning estimate based on historical per-claim timings and bounded
run deadlines, not a new measurement. Run a, b and c sequentially as shown. Model
outputs may vary even though the saved pages are fixed.

### 4. Trusted scoring

```sh
uv run python scripts/score_trusted.py "evals/runs/${RUN_DATE}-baseline-qwen235/" "evals/runs/${RUN_DATE}-replay-qwen235-a" "evals/runs/${RUN_DATE}-replay-qwen235-b" "evals/runs/${RUN_DATE}-replay-qwen235-c" evals/runs/20261116-tuning-qwen235 evals/runs/20261116-tuning-decision-gate --output "evals/runs/${RUN_DATE}-README.md"
```

Usually seconds. Prints and saves a table of true/false answers, right answers among
those, all matches (including `cannot_settle`) out of 77, Wilson 95% intervals, token
usage for the included subset, and invalid/missing-quote downgrade counts. It lists
wrong and missing answers and pairwise disagreements. Missing results count as
**no answer**, not `cannot_settle`. Unknown token usage is flagged. Historical runs
contain 80 claims; their three excluded claims do not enter any count here.

The 95% intervals describe one run's match proportion, not repeatability. To report
how far apart replay runs a/b/c are, quote their pairwise answer disagreements and
total-match gaps from the report. Do not treat one small score difference as proof
of improvement. Retrieval used different processes in the historical runs, so their
comparison is descriptive rather than a controlled replay experiment.

## Preserve every attempt and send back the results

- Perform each named run once and keep its folder. Never rerun to get a better number.
- If a run fails for a technical reason, keep its entire folder and note the failure.
  Repeat under a new name, such as `-technical-retry-1`, and include both attempts in
  the scoring command. Do not use `--resume` for this protocol, overwrite a folder,
  or remove an unfavorable run. A provider error can leave some claims unanswered.
- Do not run the source-check judge or any heldout evaluation.
- After finishing, create a new branch for the output artifacts, commit the new run
  folders and the dated README, push that branch, and open a pull request. Explain
  all incomplete runs. Do not merge it as part of this procedure. The repository
  ignores SQLite files and pipeline snapshots: retain those locally, and include
  the ignored snapshot JSON explicitly in the artifact commit so the evidence
  offered in replay can be inspected. Do not commit credentials or dotenv files.
- Send back the scoring table, retrieval counts, pairwise spread across the three
  replay runs, baseline downgrade count (`manifest.json` → `downgraded`, including
  absent/invalid quotes), and anything that failed. Include the revision and PR link.

`--ids` on the baseline and replay commands is for explicitly authorized diagnostics
on included tuning claims, not for this 77-claim protocol. Every production command
above deliberately leaves it unset. The trusted score denominator remains 77 even
when a folder contains fewer results.
