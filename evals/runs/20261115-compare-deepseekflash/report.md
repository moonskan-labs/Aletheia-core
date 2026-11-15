# Batch report: deepseek-ai/DeepSeek-V4.1-Flash-1017

- Revision 1a93f9f, 10 of 10 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Verdict matches label (conflict group excluded): 0/10 (0%).
- Verdict matches label (all claims): 0/10 (0%).

## How runs ended

- failed / provider_failure: 4
- partial / semantic_rejection: 3
- partial / invalid_task_output: 1
- partial / deadline_exceeded: 1
- unsupported_method / unsupported_method: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| comparison: decided/false | 1 | 0 | none 1 |
| comparison: decided/true | 2 | 0 | none 1, unable_to_decide/insufficient_evidence 1 |
| direct_fact: decided/almost | 2 | 0 | none 1, unable_to_decide/insufficient_evidence 1 |
| direct_fact: decided/false | 2 | 0 | none 1, unable_to_decide/insufficient_evidence 1 |
| direct_fact: decided/true | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| insufficient: unable_to_decide/insufficient_evidence | 1 | 0 | none 1 |

## Source check

- Cited statements: 0. Passage exists on the cited page with matching hashes: 0/0.
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 0/0, partly 0/0, not supported 0/0.
- Labelled source: absent 7, same_site 2, same_page 1.
- Explanation against the labelled source: None 10.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 4 (t001, t004, t005, t017)
- provider or limit: 4 (t002, t006, t011, t016)
- passage reading: 1 (t013)
- interpretation: 1 (t020)

## Cost of a run

- Seconds per claim: median 93, max 236.
- Model calls per claim: mean 7.2; search calls: mean 4.2; pages extracted: mean 2.7.
- Tokens: 285,586 in runs that produced a result.
