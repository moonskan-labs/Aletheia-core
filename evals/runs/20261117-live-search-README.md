# Live search: summary of the Nov 17 runs (issue #33)

Every run here used **live Tavily search** (no `--replay-evidence`) and the simple loop
(`ALETHEIA_PIPELINE=simple`, `ALETHEIA_PROVIDER_TIMEOUT_SECONDS=120`,
`ALETHEIA_MODEL_MAX_OUTPUT_TOKENS=16384`, parallel 4). The model received only the claim text.
Source URLs and labels stay in the scorer (`BatchClaim.request()` returns `{"claim": ...}`).

## Results

**77 trusted tuning claims** (`scripts/score_trusted.py`):

| Run | Model | Search | True/false answers | Right among those | Total matches |
| --- | --- | --- | ---: | ---: | ---: |
| 20261116-simple-gptoss120-a | gpt-oss-120b | saved pages | 59/77 | 53/59 | 59/77 (77%) |
| 20261117-simple-live-gptoss120-a | gpt-oss-120b | live | 61/77 | 54/61 | 59/77 (77%) |
| 20261117-simple-live-dsv4pro-a | DeepSeek-V4-Pro-0813 | live | 64/77 | 60/64 | **66/77 (86%)** |

**200-claim sheet** (`evals/claims/claims-20261117-200.csv`; `scripts/score_sheet.py`):

| Run | Model | True/false answers | Right among those | Total matches |
| --- | --- | ---: | ---: | ---: |
| 20261117-s200-live-gptoss120-a | gpt-oss-120b | 171/200 | 161/171 | **182/200 (91%)** |
| 20261117-s200-live-dsv4pro-a | DeepSeek-V4-Pro-0813 | still running; added to this PR when done | | |

The 200-claim totals use the sheet after two label corrections (see its README). With the
labels as first written, gpt-oss-120b scored 180/200. The new sheet is mostly stable,
well-known facts, so it is easier than the 77 trusted claims; don't compare across sets.

Each model has **one run** per set. The earlier 3-run study measured run-to-run noise of
about 3 claims on the 77 (`20261116-improvements-README.md`, saved pages). DeepSeek's 7-claim
lead on the 77 is larger than that, but it is still one run.

## Where the misses come from

Each run folder has a `diagnosis.csv` with one row per miss. For each, the full text of the
pages the run read was checked for the answer.

| Run | Misses | Search never read the answer | Answer read, verdict wrong | Time limit (150 s) |
| --- | ---: | ---: | ---: | ---: |
| gpt-oss-120b, 77 | 18 | 5 | 12 | 1 |
| DeepSeek V4 Pro, 77 | 11 | 0 | 6 | 5 (answer already read in 3, not read in 1, unclear in 1) |
| gpt-oss-120b, 200 | 18 | 0 | 14 (3 with debatable labels) | 1 |

- **Search is not the main problem.** Live search scored the same as saved pages for
  gpt-oss-120b (59/77). On the 200-claim sheet, every miss had the answer on a page it read.
- **Judging is, for gpt-oss-120b.** On the 77, it treated another agency's estimate as a
  contradiction (all five `x-` population claims), held out over one detail, or had its
  verdict withdrawn by the verdict-vs-quotation check. DeepSeek got all five population
  claims right.
- **Quotations rejected on easy claims.** On the 200, 6 easy claims (ISS, Bitcoin, WTO,
  JPEG, Kazakhstan, Rio 2016) ended as cannot_settle. The answer was on most of the pages
  read, but no quotation the model returned matched a page word for word. Rejected
  quotations are not saved, so the cause is not visible in the records.
- **Time is the cost of DeepSeek.** Median 40 s per claim (gpt-oss-120b: about 17 s); 5 of 77
  hit the 150 s limit, and in at least 3 the answer was already on a page read. It used
  0.85M input + 0.18M output tokens on the 77 (about $1.84 at Nebius list prices), against
  0.94M + 0.11M for gpt-oss-120b (about $0.21).

## Suggested next steps (issue step 4, not done here)

1. **Time limit.** Extract pages in parallel, or shorten the per-extract timeout. Some
   extractions take about 56 s each, one after another. This matters most for DeepSeek.
2. **Save rejected quotations** in the run record, then fix whatever makes the word-for-word
   match fail on easy claims.
3. **Judge prompt:** a different estimate is not a contradiction; a missing detail is not
   cannot_settle when the rest is decided; the absence of a figure is cannot_settle, not false.
4. Consider DeepSeek V4 Pro as the default model if a second run confirms the lead.

## Files

- `20261117-simple-live-gptoss120-README.md`: the first live run, with its diagnosis.
- Run folders: `20261117-simple-live-gptoss120-a`, `20261117-simple-live-dsv4pro-a`,
  `20261117-s200-live-gptoss120-a` (and `20261117-s200-live-dsv4pro-a` when done). Each
  holds the claim records, labels, manifest, scores and `diagnosis.csv`. Page text (`db/`,
  `snapshots/`) is not committed.
