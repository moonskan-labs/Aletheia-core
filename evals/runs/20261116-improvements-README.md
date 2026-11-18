# Measured fixes on saved pages: what was tried and what the numbers show

Date: 2026-11-16. Model for every run: `Qwen/Qwen3-235B-A22B-Instruct-2507`,
`ALETHEIA_NEBIUS_THINKING=default`, parallelism 6. Every run used only the saved pages
in `evals/evidence/` and the 77 trusted tuning claims. No heldout claim was run.

**Result: two changes were tried and neither was kept. The code under `scripts/`,
`src/` and `tests/` is the same as at the start (`b931edf`).** The single-call baseline
stays at 62.3 matches of 77 on the average of three runs.

## Step 1: the numbers and the path

| System | Answers given (true or false) | Right among those | Total matches |
| --- | ---: | ---: | ---: |
| Baseline, one call (`20261115-baseline-qwen235`) | 66/77 | 56/66 | 62/77 |
| Pipeline replay a | 44/77 | 38/44 | 44/77 |
| Pipeline replay b | 37/77 | 33/37 | 39/77 |
| Pipeline replay c | 40/77 | 34/40 | 40/77 |

- Pipeline score (average total matches of the three replays): **41.0**
- Noise (highest minus lowest replay): **5**
- Baseline total matches: **62**, which is at least 41.0 − 5 = 36.

**Path A (simplify): the single-call baseline is the system under test.** It was
changed only in `scripts/baseline_verdict.py` and `src/aletheia/trusted_evaluation.py`,
and it is not wired into the product API.

The baseline had one run, and the keep rule needs three runs of the system before a
change. Two more runs of the unchanged baseline were made under new names
(`20261116-baseline-qwen235-b` and `-c`). The three unchanged runs:

| Unchanged baseline | Answers given | Right among those | Total matches |
| --- | ---: | ---: | ---: |
| `20261115-baseline-qwen235` | 66/77 | 56/66 | 62/77 |
| `20261116-baseline-qwen235-b` | 67/77 | 58/67 | 64/77 |
| `20261116-baseline-qwen235-c` | 65/77 | 55/65 | 61/77 |
| Average | 66.0/77 (86%) | 169/198 (85.4%) | **62.3/77** |

Noise of the before-runs: 64 − 61 = **3**. A change is kept only if the average total
matches rise by more than 3 and the share of right answers falls by no more than two
points.

## Step 2: where the baseline loses

From the 15 claims the first baseline run got wrong or did not answer, read one by one
in `20261115-baseline-qwen235/claims/`. A claim is in one group only.

| Group | Count | Claim ids |
| --- | ---: | --- |
| a) the saved pages do not contain the answer | 3 | x-04, t-12, f-20 |
| b) the pages contain the answer and it was misread | 2 | a-06, a-19 |
| c) right answer reached, then downgraded | 1 | a-01 |
| d) comparison claims that did not resolve | 4 | c-04, c-06, c-12, c-15 |
| e) judged false because another source gives a different figure | 3 | x-01, x-08, u-08 |
| f) "most of" / "every" / "all" claims | 1 | g-08 |
| g) other: the one call ran past its 45-second limit, so no answer | 1 | g-04 |

Notes from reading them:

- **Group a.** The exact figure or the named page is not in the saved pages (checked by
  searching the saved text for the figure). f-20 answered false from a page that gives
  a different count, and its quote did not validate.
- **Group b.** a-06: the claim swaps who was sent to join whom, and the answer was true.
  a-19: the written reason ends with "the verdict should be false" but the verdict field
  says true.
- **Group c.** a-01: the answer was false and right; all four quotes were rejected
  because the model changed the quotation marks inside them.
- **Group d.** In all four, the reason text states both values correctly (405 and 501;
  $15 million and $10 million; 1 August and 24 September; Nigeria above Brazil), and the
  verdict then goes the wrong way. In c-06 and c-12 the reason itself says "the claim is
  false" while the verdict field says true. For c-12 the saved pages do not contain
  Brazil's World Bank 2024 figure.
- **Group e.** x-01 and x-08 were judged false from a rounded figure or a figure for a
  different date from a different source. The exact figures of x-01 and x-08 are not in
  the saved pages, so the best possible answer without search is cannot_settle, which
  still does not match the label (true). Only u-08 could become a match.
- Across the three unchanged runs, 13 claims are wrong in at least two runs: a-01, a-06,
  a-09, c-04, c-06, c-12, c-15, g-08, t-12, u-08, x-01, x-04, x-08. Eight more are wrong
  in one run only.

Order by size: comparisons (4), then estimates (3). Groups c and f have fewer than
three claims, so candidates 3 and 4 were skipped as the instructions say.

## Results table

| System state | Answers given (avg of 3) | Right among those | Total matches (avg) | The three runs | Kept |
| --- | ---: | ---: | ---: | --- | --- |
| Starting point: unchanged baseline | 66.0/77 | 169/198 (85.4%) | 62.3/77 | 62, 64, 61 (spread 3) | — |
| Change 1: comparisons decided in code | 58.7/77 | 150/176 (85.2%) | 56.0/77 | 58, 54, 56 (spread 4) | **No** |
| Change 2: estimates rule | 65.3/77 | 168/196 (85.7%) | 61.7/77 | 60, 61, 64 (spread 4) | **No** |
| End: unchanged baseline (both reverted) | 66.0/77 | 169/198 (85.4%) | 62.3/77 | 62, 64, 61 | — |

Full scoring tables: `20261116-fix1-comparisons-README.md` and
`20261116-fix2-estimates-README.md`.

## Change 1: comparisons decided in code — tried, not kept

Commit `5d9c524`, reverted by `bc70e22`. Runs: `20261116-fix1-comparisons-a`, `-b`, `-c`.

**What it does.** The model was asked to fill a `comparison` (each side's value, unit
and its own word-for-word quote, and the relation the claim asserts) when a claim
compares two directly stated numbers or dates. Code then compared the two values and
set the verdict, with cannot_settle if a value or quote was missing or the units
differed.

**Why not kept.** Average total matches fell from 62.3 to 56.0, a drop of 6.3 when a
rise of more than 3 was required. What the saved results show:

- c-15 became right in all three runs (the dates were compared in code).
- c-04 and c-06 stayed wrong: the model reported the right values and then chose a
  relation that agreed with the values instead of the relation the claim asserts, so
  code confirmed the wrong verdict.
- Four comparison claims that were right before became cannot_settle in all three runs
  (c-01, c-13, c-18, c-19): a side's quote was not word for word, so the side did not
  count, or (c-01) the two sides were given different unit names.
- The model filled `comparison` on 8 to 10 non-comparison claims per run (for example
  comparing the claim's figure with the page's figure). Most of those became
  cannot_settle; t-08, t-23, t-24 and x-02 were right before and wrong after.

## Change 2: estimates rule — tried, not kept

Commit `3a11fd3`, reverted by `223c3d6`. Runs: `20261116-fix2-estimates-a`, `-b`, `-c`.

**What it does.** A paragraph added to the instructions: for a claim about an estimate
or a reported figure, a different figure contradicts it only if the pages show it is
the same estimate (same source, date and scope); a figure from another source, date,
edition or scope is context, and the answer is then cannot_settle. No code decision
changed.

**Why not kept.** Average total matches went from 62.3 to 61.7. The three claims it
was written for (x-01, x-08, u-08) were still answered false in all three runs. Run b
had three claims with no answer for technical reasons (g-04 time limit, f-25, u-10);
even if the two unusual ones had both matched, the average would be 62.3, still not
more than 3 above the starting point, so no technical retry was run.

## Stop

Two changes in a row were not kept, so no further change was made. The first stop
condition is not met: 85.4% of true/false answers are right (90% needed); 86% of claims
get a true or false answer (70% needed).

## Claims still wrong at the end

The end state is the unchanged baseline. Using the first run's 15 losses:

- **Group a, needs better search: 3** (x-04, t-12, f-20). In addition, x-01 and x-08
  (group e) and c-12 (group d) cannot become right from these pages, because the exact
  figure is not saved. That makes **6 claims that need better saved pages or search**.
- Group b: 2 (a-06, a-19). Group c: 1 (a-01). Group d: 4 (c-04, c-06, c-12, c-15).
  Group e: 3 (x-01, x-08, u-08). Group f: 1 (g-08). Group g: 1 (g-04).

Not measured here, noted from the reading: in a-19, c-06 and c-12 the reason text
reaches the right conclusion and the verdict field disagrees with it. The answer format
asks for the verdict before the reason. Asking for the reason first is a candidate for a
later measured change; it was not one of the four candidates in this task, so it was not
tried.

## Tokens

| Runs | Total tokens |
| --- | ---: |
| Two extra unchanged baseline runs | 1,453,698 |
| Change 1, three runs | 2,305,807 |
| Change 2, three runs | 2,171,311 |
| **All eight runs made in this task** | **5,930,816** |

5,741,147 prompt and 189,669 completion tokens, plus unknown usage for the 6 claims that
ended without an answer. At the list price in the Nov 16 handoff ($0.20 / $0.60 per
million) that is about $1.26; this is a calculation, not a billed amount.

## What failed, and what could not be done as written

- **Tests on this machine.** The instructions expect 540 passed, 1 xfailed. On this
  Windows machine the suite needs `-o addopts="-ra --allow-hosts=127.0.0.1"` and
  `PYTHONUTF8=1`; with those it gives 538 passed, 1 xfailed and 2 failed
  (`test_b0006_final_check_diagnostics_and_bounded_repair[True]` and `[False]`: the
  pipeline's diagnostic file is not written on Windows). CI for `b931edf` passes on
  Linux. The two failures are in pipeline code this task did not touch, and they are the
  same before and after each change. `scripts/check_research_test_sensitivity.py` passed
  with `PYTEST_ADDOPTS=--allow-hosts=127.0.0.1`.
- **No branch held the measurement results.** The baseline, the three replays and
  `20261115-README.md` were uncommitted files on top of `b931edf`
  (`eval/replay-and-baseline`). They are committed on this branch as its first commit,
  and the pull request targets `eval/replay-and-baseline`.
- **The API key.** The runbook expects `NEBIUS_API_KEY` in the environment; it was not
  set. Runs were started with `uv run --env-file <path outside the repository>`, so `uv`
  loaded the key. The file was not opened, read or printed.
- **Technical failures inside runs.** A claim whose call failed is kept as "no answer",
  as in the original baseline run: g-04 (time limit) in four of the nine one-call runs,
  f-22 once, f-25 and u-10 once. No run was repeated.
- **Change 2 has no offline test that it "does not fire"** on unrelated claims, because
  it is instruction text only. Its test checked that the rule is general text with no
  digits and that no code decision changed.
- Snapshots and databases of the replay runs were not committed, as instructed. The
  runbook asks for snapshot JSON to be committed; the task instructions took priority.
