# Simple loop with live search, 77 trusted claims (Nov 17)

First measurement of the simple loop with **live Tavily search**: no `--replay-evidence`, so
the agent found its own pages. Every earlier simple-loop number read pages saved in
`evals/evidence/`. Issue #33, steps 2a and 3.

- Run: `20261117-simple-live-gptoss120-a`, 2026-11-17, revision `53d2108` (clean tree).
- Model `openai/gpt-oss-120b`, `ALETHEIA_PIPELINE=simple`, `ALETHEIA_RESEARCH_ENABLED=true`,
  `ALETHEIA_PROVIDER_TIMEOUT_SECONDS=120`, `ALETHEIA_MODEL_MAX_OUTPUT_TOKENS=16384`, parallel 4.
- Claims: the 77 `included=yes` rows of `evals/claims/trusted-tuning-20261116.csv`, read from
  `evals/claims/claims-20261115.csv`. Scored with `scripts/score_trusted.py`.
- Replay was off. A live manifest has no `"replay"` key; the runner reads it as `false`
  (`scripts/evaluate_research.py`, resume check). The manifest has `"live": true` and no
  `evidence_directory`.
- `db/` and `snapshots/` (110 MB, including full page text) are not committed, as in earlier runs.

```sh
ALETHEIA_RESEARCH_ENABLED=true ALETHEIA_PIPELINE=simple ALETHEIA_PROVIDER_TIMEOUT_SECONDS=120 \
ALETHEIA_MODEL_MAX_OUTPUT_TOKENS=16384 uv run --locked python scripts/evaluate_research.py \
  --claims-csv evals/claims/claims-20261115.csv --ids "<the 77 ids>" --batch --live \
  --pipeline simple --model openai/gpt-oss-120b --output evals/runs/20261117-simple-live-gptoss120-a
```

## Result: live search scores the same as saved pages, 59/77

| Run | Search | True/false answers | Right among those | Total matches | 95% interval | Tokens |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| 20261116-simple-gptoss120-a | saved pages | 59/77 | 53/59 (90%) | 59/77 (77%) | 66–85% | 809,970 |
| 20261117-simple-live-gptoss120-a | **live** | 61/77 | 54/61 (89%) | 59/77 (77%) | 66–85% | 1,053,101 |

Same total, but not the same claims: 19/77 answers differ. Live fixed 8 saved-page misses
(t-02, f-01, c-01, t-05, g-04, x-01, g-05, t-24) and missed 8 claims the saved-page run got
(u-02, c-04, a-07, x-02, x-05, x-07, t-21, c-18). 10 claims are wrong in both. This is
**one run each**, so the tie is only "no visible loss from live search", not a precise number.

Live used 30% more tokens. In total it made 304 Tavily searches, 561 page extractions and 268
model calls. Every claim completed, except c-18 and f-20,
which stopped at the 150 s time limit. Cost: tokens only; the manifest gives no price.

## Diagnosis of the 18 live misses (step 3)

For every miss, we searched the full text of the pages the live run read (from the run's
snapshots) for the expected answer. Per-claim detail: `20261117-simple-live-gptoss120-a/diagnosis.csv`.

| Cause | Count | Claims |
| --- | ---: | --- |
| (a) Search never read a page containing the answer | 5 | f-11, c-12, x-04, x-08, f-20 |
| (b) The answer was in a page read, but the verdict was wrong | 12 | g-01, u-02, c-04, a-06, a-07, t-12, x-02, x-05, x-07, t-21, u-08, a-16 |
| (c) The answer was in a page read, but time ran out before judging | 1 | c-18 |

**Judging, not search, is the larger problem: 12 of 18 misses.** The 12 judging misses group as:

- **Too strict about one detail (4):** g-01 ("in Stockholm"; medicine is announced in Solna),
  x-02 ("July"), c-04 (405 and 501 both read, but they were not compared), and t-21, where the
  answer was on three pages but no quotation was word for word, so none remained.
- **Verdict withdrawn by the verdict-vs-quotation check (3):** a-06, a-07, t-12. In each, the
  trusted source page itself was read.
- **A different statistic read as a contradiction (2):** x-05 and x-07 read the exact World Bank /
  Stats NZ figure but answered false from another estimate. x-04 and x-08 (search misses)
  failed the same way.
- **Answering false where the right answer is cannot_settle (2):** u-02, u-08.
- **Legal reasoning (1):** a-16 (same miss on saved pages).

The 5 search misses are narrow: a specific document (Oregon's 2025 bulletin, the IOC final
report) or the World Bank series for a specific country (FRED was never read for any `x-`
claim). Live search read the exact trusted source URL on only 17/77 claims, and its site on
43/77, yet still got 59 right. So exact-URL agreement understates how often search finds a
usable page.

## What this suggests for step 4 (not done here)

1. **Page extraction time.** 8 extractions took about 56 s each, and they run one after another.
   That cost c-18 its verdict (answer already read) and cut f-20's second round short. A shorter
   per-extract timeout, or extracting in parallel, is the cheapest fix.
2. **Population claims (`x-`).** Prefer the dataset the claim names (World Bank / FRED) in query
   planning, and tell the judge that a different agency's estimate does not contradict it.
3. Most of the remaining misses are in the judge prompt, not retrieval: give rules for
   comparing numbers, partial detail mismatch, and treating absence as cannot_settle.

Under the 3-run keep rule, any change still needs 3 live runs on each side, because live search
adds its own run-to-run variance on top of the model's.
