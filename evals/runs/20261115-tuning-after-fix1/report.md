# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision f5ccdf1, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Verdict matches label (conflict group excluded): 4/73 (5%).
- Verdict matches label (all claims): 8/80 (10%).

## How runs ended

- partial / semantic_rejection: 53
- partial / invalid_task_output: 16
- needs_clarification / None: 6
- partial / budget_exhausted: 3
- failed / invalid_task_output: 2

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | none 3, unable_to_decide/insufficient_evidence 2, unable_to_decide/conflicting_evidence 2 |
| comparison: decided/false | 7 | 0 | unable_to_decide/insufficient_evidence 6, unable_to_decide/conflicting_evidence 1 |
| comparison: decided/true | 6 | 0 | unable_to_decide/insufficient_evidence 5, none 1 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 4 | unable_to_decide/conflicting_evidence 4, unable_to_decide/insufficient_evidence 3 |
| direct_fact: decided/almost | 13 | 0 | unable_to_decide/conflicting_evidence 8, unable_to_decide/insufficient_evidence 5 |
| direct_fact: decided/false | 17 | 0 | unable_to_decide/insufficient_evidence 11, unable_to_decide/conflicting_evidence 6 |
| direct_fact: decided/true | 16 | 0 | unable_to_decide/insufficient_evidence 11, unable_to_decide/conflicting_evidence 4, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 4 | unable_to_decide/insufficient_evidence 4, none 3 |

## Source check

- Cited statements: 6. Passage exists on the cited page with matching hashes: 6/6 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 2/6 (33%), partly 3/6 (50%), not supported 1/6 (17%).
- Labelled source: absent 45, same_site 17, same_page 11, no_label_source 7.
- Explanation against the labelled source: None 78, agrees 2.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 54 (t-02, t-03, f-01, f-02, a-01, c-01, g-01, t-05, t-06, f-04, f-05, a-03, a-04, g-02, t-08, t-09, f-07, f-08, a-06, a-07, c-06, t-11, t-12, f-10, f-11, a-09, g-04, x-01, x-05, t-14, f-13, f-14, a-10, t-17, t-18, f-16, f-17, a-12, a-13, c-16, g-07, t-20, t-21, f-19, a-15, t-23, f-22, a-16, a-18, c-19, t-24, f-23, f-25, a-19)
- passage reading: 9 (c-03, c-04, c-07, c-09, c-10, c-12, c-15, f-20, c-18)
- interpretation: 8 (u-01, u-04, t-15, c-13, g-05, u-07, g-08, g-10)
- source selection: 1 (x-04)

## Cost of a run

- Seconds per claim: median 69, max 132.
- Model calls per claim: mean 11.9; search calls: mean 5.8; pages extracted: mean 4.5.
- Tokens: 6,150,128 in runs that produced a result.
