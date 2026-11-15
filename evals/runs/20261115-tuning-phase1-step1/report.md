# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision d6bac39, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 16/73 (22%).
- Verdict matches label (all claims): 21/80 (26%).
- Excluding conflict and arguable labels: 16/69 (23%).
- Arguable labels, reported separately: 5/11 (45%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.

## How runs ended

- partial / semantic_rejection: 37
- completed / evidence_sufficient: 18
- partial / invalid_task_output: 11
- partial / budget_exhausted: 8
- needs_clarification / None: 4
- failed / invalid_task_output: 2

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | decided/false 3, unable_to_decide/insufficient_evidence 3, none 1 |
| comparison: decided/false | 6 | 1 | unable_to_decide/insufficient_evidence 4, decided/false 1, none 1 |
| comparison: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 6, none 1 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 5 | unable_to_decide/conflicting_evidence 5, decided/true 1, unable_to_decide/insufficient_evidence 1 |
| direct_fact: decided/false | 30 | 6 | unable_to_decide/conflicting_evidence 18, decided/false 6, unable_to_decide/insufficient_evidence 5, none 1 |
| direct_fact: decided/true | 16 | 5 | unable_to_decide/conflicting_evidence 6, decided/true 5, none 2, unable_to_decide/insufficient_evidence 2, decided/false 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 4 | unable_to_decide/insufficient_evidence 4, decided/false 2, unable_to_decide/conflicting_evidence 1 |

## Source check

- Cited statements: 62. Passage exists on the cited page with matching hashes: 62/62 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 20/62 (32%), partly 35/62 (56%), not supported 7/62 (11%).
- Labelled source: absent 52, same_site 12, same_page 9, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 38 (f-01, f-02, a-01, t-05, f-05, a-03, a-04, c-04, t-09, f-07, f-08, a-06, a-07, t-12, a-09, c-10, g-04, x-08, t-14, t-15, f-13, a-10, t-17, f-16, f-17, a-13, c-15, g-07, f-19, a-15, c-18, u-08, a-16, a-18, t-24, f-23, a-19, g-10)
- passage reading: 15 (t-03, g-01, c-03, g-02, t-08, c-07, u-04, c-09, u-05, c-12, x-07, c-13, f-20, g-08, c-19)
- interpretation: 6 (t-02, c-01, g-05, c-16, t-21, f-22)
- bad citations: 1 (f-14)

## Cost of a run

- Seconds per claim: median 66, max 135.
- Model calls per claim: mean 11.7; search calls: mean 6.0; pages extracted: mean 4.6.
- Tokens: 6,177,284 in runs that produced a result.
