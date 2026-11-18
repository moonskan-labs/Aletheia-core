# Other models on the single-call baseline: one run each

Date: 2026-11-16. The unchanged single-call baseline (`scripts/baseline_verdict.py` at
`0ecb52e`, same code as `b931edf`) was run once on each of three other Nebius models,
on the 77 trusted tuning claims and the saved pages in `evals/evidence/`. No heldout
claim was run. No code changed.

**Result: no model scored more total matches than the current one.** All three gave
fewer true/false answers and were right more often on the ones they gave.

## Results

| Model | Run | Answers given (true or false) | Right among those | Total matches |
| --- | --- | ---: | ---: | ---: |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` (current, average of 3) | `20261115-baseline-qwen235`, `20261116-baseline-qwen235-b`, `-c` | 66.0/77 | 169/198 (85.4%) | 62.3/77 (62, 64, 61) |
| `openai/gpt-oss-120b` | `20261116-model-gptoss120` | 57/77 | 53/57 (93.0%) | 59/77 |
| `deepseek-ai/DeepSeek-V4.1-Flash-1017` | `20261116-model-dsv41flash` | 56/77 | 53/56 (94.6%) | 59/77 |
| `deepseek-ai/DeepSeek-V4-Pro-0813` | `20261116-model-dsv4pro-b` | 58/77 | 54/58 (93.1%) | 60/77 |
| `deepseek-ai/DeepSeek-V4-Pro-0813`, technically failed | `20261116-model-dsv4pro` | 47/77 | 46/47 | 50/77 |

The spread of the three unchanged Qwen runs is 3 total matches. Each other model has
one run, and its total matches are 2 to 3 below the Qwen average, so the totals do not
separate the models.

What the saved results show:

- Each other model answered cannot_settle on 19 to 20 claims; the Qwen runs did so on
  10 to 11.
- t-02, c-01, g-01, t-05 and f-11 were right in the first Qwen run and cannot_settle on
  all three other models.
- c-04, c-06, c-15 and g-08 were wrong in the first Qwen run and right on all three
  other models. g-04, which ran past the 45-second limit there, was answered.
- t-12, x-04, f-20, x-01, x-08 and c-12 were wrong on every model. These are the six
  claims whose answer is not in the saved pages.

## Settings that differ from the Qwen runs

- `ALETHEIA_PROVIDER_TIMEOUT_SECONDS=120` (Qwen runs: 45) and
  `ALETHEIA_MODEL_MAX_OUTPUT_TOKENS=16384` (Qwen runs: 4096), because these models
  reason before answering. Longest single claim: 10 seconds on gpt-oss-120b, 67 on
  DeepSeek V4.1 Flash.
- `ALETHEIA_NEBIUS_THINKING=default` and parallelism 6, as before. The code allows the
  thinking switch only for one other model, so each model ran with its own default.

## Technical failures

- `20261116-model-dsv4pro`: 14 claims ended with a network error (the local internet
  connection dropped during the run). The run is kept, and the model was run once more
  as `20261116-model-dsv4pro-b`, which had no failures.
- `20261116-model-dsv41flash`: f-01 ended with an invalid response and is counted as no
  answer.
- Three 3-claim format checks were made first (`*-probe` folders: t-02, c-04, a-06 on
  each model) to confirm each model accepts the structured answer format. They are not
  part of the scores.

## Tokens and cost

Prices are from the Nebius model list on 2026-11-16, per million tokens. The costs are
calculated from token counts, not billed amounts.

| Run | Prompt tokens | Completion tokens | Price in / out | Cost |
| --- | ---: | ---: | --- | ---: |
| `20261116-model-gptoss120` | 654,695 | 51,246 | $0.15 / $0.60 | $0.13 |
| `20261116-model-dsv41flash` | 665,919 | 149,055 | $0.30 / $1.20 | $0.38 |
| `20261116-model-dsv4pro` | 550,018 + unknown for 14 claims | 84,937 | $1.32 / $3.96 | $1.06 + unknown |
| `20261116-model-dsv4pro-b` | 669,307 | 111,741 | $1.32 / $3.96 | $1.33 |

Total about $2.90, plus the three format checks and the unknown usage of the failed
claims. One Qwen run is about $0.15.
