# Model comparison, Nov 15, 2026

Same 10 claims (t001, t002, t004, t005, t006, t011, t013, t016, t017, t020 from
docs/evaluation/proposed-claims.json), one run per model, revision 1a93f9f, three claims
in parallel per model. Every run is kept in the four folders beside this file. Prices are
from the live Nebius model list on Nov 15 (USD per million input / output tokens).

| model | price | ended with a result | verdict matches label | median seconds | what went wrong |
|---|---|---|---|---|---|
| nvidia/Nemotron-3_5-Lightning (thinking disabled) | 0.06 / 0.24 | 10 of 10 | 1 | 59 | all 10 ended partial with no verdict: 6 final-check rejections, 4 source assessments failed validation |
| Qwen/Qwen3-30B-A3B-Instruct-2507 | 0.10 / 0.30 | 7 of 10 | 1 | 58 | 3 claims refused as unsupported method (two are plain comparisons); 19 of 31 source assessments failed validation |
| deepseek-ai/DeepSeek-V4.1-Flash-1017 | 0.30 / 1.20 | 5 of 10 | 0 | 93 | 4 runs failed on output cut off at the token limit (it spends tokens on reasoning); slow |
| zai-org/GLM-5.3-Flash | 0.15 / 0.50 | 0 of 10 | 0 | 75 | every call timed out at the first step; a one-line test call took 67 seconds |

No provider rate limiting was seen (every completed call returned 200).

## Pick: nvidia/Nemotron-3_5-Lightning, thinking disabled

It is the cheapest, it was the only model where every run got through interpretation,
planning, search and reading, and its source assessments passed validation more often than
Qwen's (40 of 68 against 11 of 31).

## What this comparison could not show

Citation quality could not be compared: only one run of the 40 published an explanation
(Qwen, t004: 3 cited statements, all passages valid, judge said 2 supported and 1 partly).
The main result is that the pipeline withholds almost every verdict on all four models,
mostly at the final check. That is a pipeline problem more than a model problem, and it is
what the 80-claim run measures next.
