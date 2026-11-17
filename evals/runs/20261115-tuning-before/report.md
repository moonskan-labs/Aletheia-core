# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision b0e838e, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Verdict matches label (conflict group excluded): 6/73 (8%).
- Verdict matches label (all claims): 6/80 (8%).

## How runs ended

- partial / semantic_rejection: 41
- partial / invalid_task_output: 23
- needs_clarification / None: 8
- partial / budget_exhausted: 3
- failed / budget_exhausted: 1
- unsupported_method / unsupported_method: 1
- failed / provider_failure: 1
- failed / invalid_task_output: 1
- partial / deadline_exceeded: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 5, none 2 |
| comparison: decided/false | 7 | 0 | unable_to_decide/insufficient_evidence 6, none 1 |
| comparison: decided/true | 6 | 0 | unable_to_decide/insufficient_evidence 6 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | unable_to_decide/insufficient_evidence 7 |
| direct_fact: decided/almost | 13 | 1 | unable_to_decide/insufficient_evidence 11, none 1, decided/almost 1 |
| direct_fact: decided/false | 17 | 0 | unable_to_decide/insufficient_evidence 12, none 5 |
| direct_fact: decided/true | 16 | 0 | unable_to_decide/insufficient_evidence 15, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 5 | unable_to_decide/insufficient_evidence 5, none 2 |

## Source check

- Cited statements: 5. Passage exists on the cited page with matching hashes: 5/5 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 5/5 (100%), partly 0/5 (0%), not supported 0/5 (0%).
- Labelled source: absent 44, same_site 19, same_page 10, no_label_source 7.
- Explanation against the labelled source: None 79, agrees 1.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 31 (t-02, f-01, g-01, t-05, t-06, a-03, a-04, t-08, t-09, a-06, c-06, t-11, t-12, x-01, x-02, x-08, t-14, f-13, f-14, t-17, t-18, f-16, f-17, a-12, a-13, g-07, t-20, f-19, t-23, a-19, g-10)
- passage reading: 25 (t-03, c-01, c-03, f-07, f-08, c-07, f-11, c-09, c-10, g-04, c-12, x-04, x-05, x-07, x-10, c-13, g-05, c-15, c-16, a-15, f-22, a-18, c-19, t-24, f-25)
- interpretation: 10 (f-02, a-01, u-02, f-04, f-05, g-02, u-05, f-20, c-18, g-08)
- source selection: 8 (c-04, a-07, f-10, a-09, t-15, t-21, a-16, f-23)

## Cost of a run

- Seconds per claim: median 68, max 133.
- Model calls per claim: mean 11.9; search calls: mean 6.1; pages extracted: mean 4.7.
- Tokens: 5,775,750 in runs that produced a result.
