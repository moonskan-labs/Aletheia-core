# Hackathon status and plan — November 17, 2026

ODSC × Nebius hackathon. Submissions close **Friday, November 20, 2026, 11:59 PM EST**
at <https://hackathon.odsc.ai/submit>. Required: inference on Nebius Token Factory,
real-time search with Tavily, a public repo with a README, and a 2–3 minute demo video.
There is no live demo day; judges score the video and the repo.

Judging weights: sourced and verifiable answers 30%, works end to end 25%,
usefulness 20%, agent design 15%, use of Token Factory and Tavily 10%.

## Where accuracy stands

**Live-search accuracy is now measured: DeepSeek V4 Pro scored 66/77 (86%),
and gpt-oss-120b scored 59/77 (77%).**

- [PR #35](https://github.com/skanvish11/Aletheia-core/pull/35) measures the simple
  loop with live Tavily search on the 77 trusted tuning claims and a separate
  200-claim sheet. The earlier 81% single-call baseline and 69–77% simple-loop
  figures used saved pages (`replay: true`); keep those distinct from live search.
  In those older manifests, `live: true` only means the model was called.
- A [second DeepSeek run reported in #33](https://github.com/skanvish11/Aletheia-core/issues/33#issuecomment-6967513778)
  also scored 66/77. It included the quotation and parallel-read fixes from #36
  and #37, so it is not an unchanged-baseline repeat. Thirteen answers differed
  between runs despite identical totals; prompt changes still need the 3-run rule.
- The second run's median was 28 s per claim, with 5/77 taking at least 100 s and
  3/77 reaching the 150 s limit. The original #35 run had a 40 s median and five
  time-outs. The rerun resumed after a Tavily credit top-up; credit-failed claims
  were rerun to obtain one clean answer per claim.
- Measurement and diagnosis are covered by #35; follow-up work remains tracked in
  [issue #33](https://github.com/skanvish11/Aletheia-core/issues/33) (Chandra).

All figures below are on the same 77 trusted tuning claims. "Right when answering" is
the share of true/false answers that were correct; the rest of the misses are mostly
`cannot_settle`.

| System | Model | Search | Correct of 77 | Right when answering | In the app? | Source |
| --- | --- | --- | ---: | ---: | --- | --- |
| Single-call baseline | Qwen3-235B | Saved pages | 62.3 (81%), avg of 3 runs | 85% | No, eval script only | [PR #29](https://github.com/skanvish11/Aletheia-core/pull/29), `evals/runs/20261116-improvements-README.md` |
| Single-call baseline | gpt-oss-120b / DeepSeek V4.x | Saved pages | 59–60 (77–78%), 1 run each | 93–95% | No | `evals/runs/20261116-models-README.md` (merged in #29) |
| Simple loop | gpt-oss-120b | Saved pages | 53–59 (69–77%), 1 run per variant | 90–96% | Yes, `ALETHEIA_PIPELINE=simple` | `evals/runs/20261116-simple-loop-versions-README.md` |
| Staged pipeline | Qwen3-235B | Saved pages | 39–44 (51–57%) | 85–89% | Yes, default | `evals/runs/20261115-README.md` |
| Staged pipeline | Qwen3-235B | **Live** | 42 (55%) | 80% | Yes | `evals/runs/20261116-tuning-qwen235` |
| Simple loop | gpt-oss-120b | **Live** | **59 (77%)** | 54/61 (89%) | Yes | [#35 run report](https://github.com/skanvish11/Aletheia-core/blob/claude/modest-pasteur-yu0542/evals/runs/20261117-live-search-README.md) |
| Simple loop | DeepSeek V4 Pro | **Live** | **66 (86%)** | 60/64 (94%) | Yes | [#35 run report](https://github.com/skanvish11/Aletheia-core/blob/claude/modest-pasteur-yu0542/evals/runs/20261117-live-search-README.md) |
| Simple loop + #36/#37 | DeepSeek V4 Pro | **Live** | **66 (86%)** | 62/67 (93%) | Fixes in open PRs | [#33 rerun](https://github.com/skanvish11/Aletheia-core/issues/33#issuecomment-6967513778) |

The saved-page study identified six claims (t-12, x-04, f-20, x-01, x-08, c-12)
whose exact answers were missing from the saved evidence. That limitation does not
apply unchanged to live search: DeepSeek answered all five population claims correctly
in #35. On the 200-claim sheet, every miss had the answer on a page read; judging
and quotation checks were the main problems.

## Component status

| Component | Status | Where / notes |
| --- | --- | --- |
| Working agent with Token Factory + Tavily | Done | Simple loop on `main` ([PR #30](https://github.com/skanvish11/Aletheia-core/pull/30)) |
| Insufficient-evidence handling | Done | `cannot_settle`, verbatim quote checks, verdict withdrawn when quotes point the other way |
| Live-search accuracy | Measured; open PR | [PR #35](https://github.com/skanvish11/Aletheia-core/pull/35); DeepSeek 66/77, gpt-oss-120b 59/77; DeepSeek rerun in #33 also 66/77 |
| Web UI with real recordings, passage links, research trace | Open PR | [PR #32](https://github.com/skanvish11/Aletheia-core/pull/32) |
| Model comparison and measured fixes on `main` | Merged | `improve/measured-fixes`: [PR #29](https://github.com/skanvish11/Aletheia-core/pull/29), based on `main` and now merged |
| Quotation matching | Open PR | [PR #36](https://github.com/skanvish11/Aletheia-core/pull/36); six targeted cases now correct, one run each; not a full accuracy estimate |
| Parallel searches and page reads | Open PR | [PR #37](https://github.com/skanvish11/Aletheia-core/pull/37); all six targeted time-outs finished within the limit; model-time limits remain |
| Public repo, no committed keys | Done | Full history scanned for Nebius/Tavily keys and `.env` files on Nov 17 |
| README Quickstart for judges | Missing | Setup is only in `docs/research-pipeline.md` and `web/README.md` |
| `.env.example` | Missing | `.gitignore` already allows it |
| Model name and Tavily usage in README | Missing | `NEBIUS_MODEL` has no default; not named in README |
| Short architecture overview of the simple loop | Missing | README describes the staged design; content exists in `docs/simple-loop.md` |
| Accuracy summary in README | Missing | Use the table above, with live numbers from issue #33 |
| Demo video (2–3 min) | Missing | |
| Submission form | Missing | |

## Plan

Each item lands as its own PR so the work stays reviewable.

| # | Work | Owner | Needed for submission? | Target |
| --- | --- | --- | --- | --- |
| 1 | This status doc | skanvish11 (with Claude) | Yes | Nov 17 |
| 2 | Review #35 (measurement, 200-claim sheet and diagnosis); review #36/#37 follow-up fixes ([issue #33](https://github.com/skanvish11/Aletheia-core/issues/33)) | Chandra | Step 1 numbers: yes | Wed Nov 18; fixes by Thu Nov 19 |
| 3 | Saved-page evidence from `improve/measured-fixes`: #29 merged into `main` | Chandra | Nice to have | Nov 18 |
| 4 | Review and merge [PR #32](https://github.com/skanvish11/Aletheia-core/pull/32) (web loop recordings) | skanvish11 | Yes | Nov 18 |
| 5 | Judge-facing README: what it is and who it is for, Quickstart, `.env.example`, model and Tavily section, simple-loop architecture, accuracy (saved-page and live side by side), failure handling; full design moved to `docs/design.md` | skanvish11 (with Claude) | Yes | Nov 18 |
| 6 | Demo video script following the rubric | skanvish11 (with Claude) | Yes | Nov 18 |
| 7 | Record the video, add the link to the README, submit the form | skanvish11 | Yes | Thu Nov 19 (a day before the deadline) |

Recommended demo configuration from the live results: `ALETHEIA_PIPELINE=simple`,
`NEBIUS_MODEL=deepseek-ai/DeepSeek-V4-Pro-0813`. DeepSeek scored 66/77 in both
reported runs versus gpt-oss-120b's 59/77. Budget for its latency: with #36/#37 the
median was about 28 s and roughly 1 in 15 claims took at least 100 s; the original
run without those fixes had a 40 s median. Review and merge those fixes before
expecting the improved timings. This is a documented recommendation, not a change
to the application's configuration.
