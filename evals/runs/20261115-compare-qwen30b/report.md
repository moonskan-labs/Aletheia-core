# Batch report: Qwen/Qwen3-30B-A3B-Instruct-2507

- Revision 1a93f9f, 10 of 10 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Verdict matches label (conflict group excluded): 1/10 (10%).
- Verdict matches label (all claims): 1/10 (10%).

## How runs ended

- partial / semantic_rejection: 5
- unsupported_method / unsupported_method: 3
- partial / invalid_task_output: 2

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| comparison: decided/false | 1 | 0 | none 1 |
| comparison: decided/true | 2 | 0 | unable_to_decide/insufficient_evidence 1, none 1 |
| direct_fact: decided/almost | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| direct_fact: decided/false | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| direct_fact: decided/true | 2 | 1 | unable_to_decide/insufficient_evidence 1, decided/true 1 |
| insufficient: unable_to_decide/insufficient_evidence | 1 | 0 | none 1 |

## Source check

- Cited statements: 3. Passage exists on the cited page with matching hashes: 3/3 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 2/3 (67%), partly 1/3 (33%), not supported 0/3 (0%).
- Labelled source: absent 9, same_site 1.
- Explanation against the labelled source: None 9, agrees 1.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 4 (t001, t002, t005, t017)
- interpretation: 3 (t006, t013, t020)
- passage reading: 2 (t011, t016)

## Cost of a run

- Seconds per claim: median 58, max 149.
- Model calls per claim: mean 7.8; search calls: mean 3.2; pages extracted: mean 2.1.
- Tokens: 367,565 in runs that produced a result.
