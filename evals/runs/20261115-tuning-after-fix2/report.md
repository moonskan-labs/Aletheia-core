# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision be71eb3, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Verdict matches label (conflict group excluded): 16/73 (22%).
- Verdict matches label (all claims): 17/80 (21%).

## How runs ended

- partial / semantic_rejection: 48
- completed / evidence_sufficient: 10
- needs_clarification / None: 9
- partial / invalid_task_output: 6
- partial / budget_exhausted: 5
- failed / invalid_task_output: 2

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 1 | unable_to_decide/insufficient_evidence 2, none 2, unable_to_decide/conflicting_evidence 2, decided/true 1 |
| comparison: decided/false | 7 | 0 | none 3, unable_to_decide/insufficient_evidence 2, decided/true 1, unable_to_decide/conflicting_evidence 1 |
| comparison: decided/true | 6 | 0 | unable_to_decide/insufficient_evidence 3, none 2, unable_to_decide/conflicting_evidence 1 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 1 | unable_to_decide/insufficient_evidence 5, decided/true 1, unable_to_decide/conflicting_evidence 1 |
| direct_fact: decided/almost | 13 | 1 | unable_to_decide/conflicting_evidence 6, unable_to_decide/insufficient_evidence 6, decided/almost 1 |
| direct_fact: decided/false | 17 | 0 | unable_to_decide/insufficient_evidence 10, unable_to_decide/conflicting_evidence 5, decided/almost 1, none 1 |
| direct_fact: decided/true | 16 | 8 | decided/true 8, unable_to_decide/conflicting_evidence 4, none 3, unable_to_decide/insufficient_evidence 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 6 | unable_to_decide/insufficient_evidence 6, unable_to_decide/conflicting_evidence 1 |

## Source check

- Cited statements: 44. Passage exists on the cited page with matching hashes: 44/44 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 13/44 (30%), partly 28/44 (64%), not supported 3/44 (7%).
- Labelled source: absent 49, same_site 15, same_page 9, no_label_source 7.
- Explanation against the labelled source: None 61, agrees 18, disagrees 1.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 44 (f-01, f-02, a-01, g-01, t-05, f-04, f-05, a-03, c-03, t-09, f-07, f-08, a-06, a-07, c-06, t-12, f-10, f-11, a-09, g-04, x-01, x-02, x-04, x-05, x-08, f-13, f-14, a-10, g-05, f-16, f-17, a-12, a-13, c-16, g-07, t-21, f-19, a-15, u-08, f-22, a-16, t-24, f-25, a-19)
- interpretation: 11 (c-04, g-02, c-09, t-15, c-13, t-17, t-18, f-20, c-18, g-08, c-19)
- passage reading: 7 (c-01, a-04, c-07, c-10, c-12, x-07, c-15)
- bad citations: 1 (t-08)
- source selection: 1 (f-23)

## Cost of a run

- Seconds per claim: median 64, max 130.
- Model calls per claim: mean 10.8; search calls: mean 5.2; pages extracted: mean 4.0.
- Tokens: 5,360,829 in runs that produced a result.
