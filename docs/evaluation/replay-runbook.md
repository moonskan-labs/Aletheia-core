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
false answer without a valid quotation becomes `cannot_settle`; technical failures
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
**no answer**, not `cannot_settle`. Failed investigations and rejected final checks
(`semantic_rejection` or `invalid_task_output`) also count as no answer, even if a
legacy artifact contains an undecided result. Valid partial abstentions remain
`cannot_settle`. This scoring correction can change newly generated reports; keep
historical reports unchanged. Unknown token usage is flagged. Historical runs
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

## Portability and quotation policy

The commands above use Bash (including Git Bash on Windows). In PowerShell, set:

```powershell
$RUN_DATE = "YYYYMMDD"
$env:ALETHEIA_NEBIUS_THINKING = "default"
```

The same `uv run` commands and double-quoted `${RUN_DATE}` paths then work in
PowerShell. Replace YYYYMMDD once; use new output names. `score_trusted.py` writes
UTF-8 to both stdout and the report file, including when stdout is redirected.

Final-check diagnostics use private POSIX permissions or a protected current-user
Windows ACL. Windows PowerShell is used to create and verify that ACL on Windows
Python 3.12 and 3.13. Permissive existing directories, symlinks and junctions are
refused; diagnostics never silently fall back to public files. If an older run left
a permissive diagnostic directory, choose a fresh run folder. Diagnostic failures
remain optional and do not change the verdict.

Baseline and simple-loop quotation matching allows whitespace and straight/curly
single/double quotation-mark differences away from numbers and within-word
punctuation. Numeric measurement marks retain their feet/inches distinction.
It does not remove punctuation, change
case, numbers or negation, or join noncontiguous text. A match must exist in both the
offered passages and the original page. The simple loop stores the page's exact
excerpt, offsets and hash rather than the model's altered quotation. Original model
answers remain in baseline artifacts. This is a quotation-integrity check, not proof
that a quotation supports a verdict; do not rewrite historical scores under this rule.

## Reference-label review still pending

“Trusted” is the historical name of the frozen scoring file, not a claim that all
labels have completed independent human review. [PR 27's preserved checklist](../../evals/claims/review-follow-up-27.md)
and [decision tracker](../../evals/claims/recheck-review-decisions.csv) record the
outstanding provenance, quote checks, human spot-checks, ambiguous wording and missing
conflict cases. They do not change the 77-claim denominator or prompt inputs.

The experimental simple pipeline from PR 30 is included in this branch but remains
off by default. These replay commands use the staged pipeline unless `--pipeline
simple` is explicitly supplied. Its saved pilot runs still contain errors on missing
or conflicting evidence; software checks are not a claim of research readiness.
