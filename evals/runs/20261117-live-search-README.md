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
| 20261117-s200-live-dsv4pro-a | DeepSeek-V4-Pro-0813 | 176/200 | 169/176 | **191/200 (96%)** |

The 200-claim totals use the sheet after two label corrections (see its README). With the
labels as first written, gpt-oss-120b scored 180/200 (DeepSeek started after the correction). The new sheet is mostly stable,
well-known facts, so it is easier than the 77 trusted claims; don't compare across sets.

Each model has **one run** per set. The earlier 3-run study measured run-to-run noise of
about 3 claims on the 77 (`20261116-improvements-README.md`, saved pages). DeepSeek's 7-claim
lead on the 77 (and 9 on the 200) is larger than that, but it is still one run per set.

## Where the misses come from

Each run folder has a `diagnosis.csv` with one row per miss. For each, the full text of the
pages the run read was checked for the answer.

| Run | Misses | Search never read the answer | Answer read, verdict wrong | Time limit (150 s) |
| --- | ---: | ---: | ---: | ---: |
| gpt-oss-120b, 77 | 18 | 5 | 12 | 1 |
| DeepSeek V4 Pro, 77 | 11 | 0 | 6 | 5 (answer already read in 3, not read in 1, unclear in 1) |
| gpt-oss-120b, 200 | 18 | 0 | 17 (3 with debatable labels) | 1 |
| DeepSeek V4 Pro, 200 | 9 | 0 | 9 (2 with debatable labels) | 0 |

- **Search is not the main problem.** Live search scored the same as saved pages for
  gpt-oss-120b (59/77). On the 200-claim sheet, every miss had the answer on a page it read.
- **Judging is, for gpt-oss-120b.** On the 77, it treated another agency's estimate as a
  contradiction (all five `x-` population claims), held out over one detail, or had its
  verdict withdrawn by the verdict-vs-quotation check. DeepSeek got all five population
  claims right.
- **Quotations rejected on easy claims.** On the 200, 6 easy claims (ISS, Bitcoin, WTO,
  JPEG, Kazakhstan, Rio 2016) ended as cannot_settle for gpt-oss-120b, and 2 (Kipchoge, Starry Night)
  for DeepSeek. The answer was on most of the pages
  read, but no quotation the model returned matched a page word for word. Rejected
  quotations are not saved, so the cause is not visible in the records.
- **Time is the cost of DeepSeek.** Median 40 s per claim (gpt-oss-120b: about 17 s); 5 of 77
  hit the 150 s limit, and in at least 3 the answer was already on a page read. It used
  0.85M input + 0.18M output tokens on the 77 (about $1.84 at Nebius list prices), against
  0.94M + 0.11M for gpt-oss-120b (about $0.21). On the 200: about $4.10 against $0.48, median
  29 s per claim against 17 s.

## Next step: make gpt-oss-120b perform like DeepSeek (issue step 4, not done here)

The question for the next PR is whether the harness around gpt-oss-120b, not the model
itself, can close most of the gap to DeepSeek V4 Pro at about 1/9 of its cost and twice its
speed.

**Where DeepSeek's lead on the 77 comes from.** It gets 11 of gpt-oss-120b's misses right.
About 9 are **judging**: both models read pages with the answer, and only gpt-oss-120b
concluded wrongly. For example, on x-05 and x-07 both read the exact population figure, and
gpt-oss-120b answered false because another agency gave a different estimate. About 2 are
**search**: on x-04 and x-08, DeepSeek's follow-up round reached the FRED / World Bank page
and gpt-oss-120b's did not, from near-identical queries, so this may be luck. On the 200-claim
sheet, DeepSeek gets most of gpt-oss-120b's misses right, including the six easy claims it lost
to the quotation check.

**Changes to try, best bets first. Each targets misses in the `diagnosis.csv` files.**

1. **Quotation matching that ignores page formatting.** Page text contains markdown
   (`**21 million**`, `[Geneva](link)`, table bars). Match the quotation's words while
   ignoring that formatting; it must still be found on the page. Also save rejected
   quotations in the run record so the remaining failures can be seen. Targets the 6 easy
   claims on the 200 (s200-022, -036, -089, -100, -120, -130) and some on the 77 (t-21,
   c-18). Deterministic and safe. Start here.
2. **Four judge-prompt rules, each taken from a real miss:**
   - A different agency's or dataset's estimate is not a contradiction; when a claim names
     its source, judge it against that source (x-05, x-07).
   - When one page disagrees with most pages read, follow the majority (s200-021, -040, -111).
   - "No page gives this exact figure" is cannot_settle, not false (u-02, u-08, s200-011,
     -090, -124, -170).
   - When the evidence rules out the claim's figure, answer false rather than holding out
     (s200-041: the Paris goal is 2 °C, not 3 °C).
3. **Higher reasoning effort for gpt-oss-120b.** It is a reasoning model. The thinking switch
   is currently allowed only for one Nemotron model (`src/aletheia/config.py`), so first
   confirm with a 3-claim test that Nebius honours a reasoning-effort setting for gpt-oss-120b.
4. **Review the verdict-vs-quotation check.** It withdrew gpt-oss-120b's verdict on a-06, a-07
   and t-12, where the trusted source page had been read. Check whether the withdrawn
   verdicts were right before changing it.
5. **Search the dataset a claim names.** When a claim cites the World Bank or a statistics
   office, add a query aimed at that dataset or FRED (x-04, x-08).
6. **Time limit.** Extract pages in parallel, or shorten the per-extract timeout; some
   extractions take about 56 s each, one after another. Costs gpt-oss-120b one claim per set,
   and matters more for DeepSeek.

**How to measure it (the existing 3-run keep rule):** run gpt-oss-120b live on the 77 twice
more, unchanged, to get a 3-run baseline and its noise. Then add one change at a time, with
3 runs each, and keep a change only if its average beats the baseline by more than the noise.
Finish with one run on the 200-claim sheet. A live 77-claim gpt-oss-120b run takes about
20 minutes and about $0.21 in model tokens (plus Tavily), so the plan is roughly 3–4 hours.
The README can then show gpt-oss-120b rising from 59/77, one kept change at a time, beside
DeepSeek's 66/77, with cost and time per claim.

## Files

- `20261117-simple-live-gptoss120-README.md`: the first live run, with its diagnosis.
- Run folders: `20261117-simple-live-gptoss120-a`, `20261117-simple-live-dsv4pro-a`,
  `20261117-s200-live-gptoss120-a`, `20261117-s200-live-dsv4pro-a`. Each
  holds the claim records, labels, manifest, scores and `diagnosis.csv`. Page text (`db/`,
  `snapshots/`) is not committed.
