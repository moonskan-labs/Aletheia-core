# Hackathon status and plan — November 17, 2026

ODSC × Nebius hackathon. Submissions close **Friday, November 20, 2026, 11:59 PM EST**
at <https://hackathon.odsc.ai/submit>. Required: inference on Nebius Token Factory,
real-time search with Tavily, a public repo with a README, and a 2–3 minute demo video.
There is no live demo day; judges score the video and the repo.

Judging weights: sourced and verifiable answers 30%, works end to end 25%,
usefulness 20%, agent design 15%, use of Token Factory and Tavily 10%.

## Where accuracy stands

**The 80% comes from saved pages, not from live retrieval.**

- None of our accuracy numbers used live search for the systems we would demo. The
  81% single-call baseline and the 69–77% simple-loop runs all ran with
  `replay: true`: the model read web pages saved ahead of time in `evals/evidence/`.
  (Those manifests also say `live: true`; that only means the model was called.)
- So they test only half the agent, **read and judge**: given good pages, the model
  decides correctly about 80% of the time.
- The other half, **finding those pages with a live Tavily search**, has never been
  measured for the simple loop. The one hint is weak: live search reached the same
  trusted source page for only 13 of 77 claims (same site: 41 of 77) in
  `evals/runs/20261116-retrieval-check` (branch `improve/measured-fixes`).
- The app does search live, so the demo works, but its real accuracy is unknown.
- The gap: measure with live search, then improve search if it is low. Tracked in
  [issue #33](https://github.com/skanvish11/Aletheia-core/issues/33) (Chandra).

All figures below are on the same 77 trusted tuning claims. "Right when answering" is
the share of true/false answers that were correct; the rest of the misses are mostly
`cannot_settle`.

| System | Model | Search | Correct of 77 | Right when answering | In the app? | Source |
| --- | --- | --- | ---: | ---: | --- | --- |
| Single-call baseline | Qwen3-235B | Saved pages | 62.3 (81%), avg of 3 runs | 85% | No, eval script only | `improve/measured-fixes`, `evals/runs/20261116-improvements-README.md` |
| Single-call baseline | gpt-oss-120b / DeepSeek V4.x | Saved pages | 59–60 (77–78%), 1 run each | 93–95% | No | `evals/runs/20261116-models-README.md` (same branch) |
| Simple loop | gpt-oss-120b | Saved pages | 53–59 (69–77%), 1 run per variant | 90–96% | Yes, `ALETHEIA_PIPELINE=simple` | `evals/runs/20261116-simple-loop-versions-README.md` |
| Staged pipeline | Qwen3-235B | Saved pages | 39–44 (51–57%) | 85–89% | Yes, default | `evals/runs/20261115-README.md` |
| Staged pipeline | Qwen3-235B | **Live** | 42 (55%) | 80% | Yes | `evals/runs/20261116-tuning-qwen235` |
| Simple loop | any | **Live** | **not measured** | — | Yes | Issue #33 |

Six claims (t-12, x-04, f-20, x-01, x-08, c-12) are wrong on every model because the
saved pages do not contain the answer: a retrieval limit, not a model limit.

## Component status

| Component | Status | Where / notes |
| --- | --- | --- |
| Working agent with Token Factory + Tavily | Done | Simple loop on `main` ([PR #30](https://github.com/skanvish11/Aletheia-core/pull/30)) |
| Insufficient-evidence handling | Done | `cannot_settle`, verbatim quote checks, verdict withdrawn when quotes point the other way |
| Live-search accuracy | **Missing** | Issue #33 |
| Web UI with real recordings, passage links, research trace | Open PR | [PR #32](https://github.com/skanvish11/Aletheia-core/pull/32) |
| Model comparison and measured fixes on `main` | Branch only | `improve/measured-fixes` has no PR |
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
| 2 | Live-search measurement, own 200-claim sheet, diagnosis, retrieval fixes if time allows ([issue #33](https://github.com/skanvish11/Aletheia-core/issues/33)) | Chandra | Step 1 numbers: yes | Wed Nov 18; fixes by Thu Nov 19 |
| 3 | PR for `improve/measured-fixes` so the saved-page evidence is on `main` | Chandra | Nice to have | Nov 18 |
| 4 | Review and merge [PR #32](https://github.com/skanvish11/Aletheia-core/pull/32) (web loop recordings) | skanvish11 | Yes | Nov 18 |
| 5 | Judge-facing README: what it is and who it is for, Quickstart, `.env.example`, model and Tavily section, simple-loop architecture, accuracy (saved-page and live side by side), failure handling; full design moved to `docs/design.md` | skanvish11 (with Claude) | Yes | Nov 18 |
| 6 | Demo video script following the rubric | skanvish11 (with Claude) | Yes | Nov 18 |
| 7 | Record the video, add the link to the README, submit the form | skanvish11 | Yes | Thu Nov 19 (a day before the deadline) |

Demo configuration until live numbers say otherwise: `ALETHEIA_PIPELINE=simple`,
`NEBIUS_MODEL=openai/gpt-oss-120b`. If Qwen3-235B wins in live runs, switch the
documented default.
