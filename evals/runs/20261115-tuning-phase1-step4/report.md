# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision b7da553, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 13/73 (18%).
- Verdict matches label (all claims): 13/80 (16%).
- Excluding conflict and arguable labels: 13/69 (19%).
- Arguable labels, reported separately: 0/11 (0%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.

## How runs ended

- partial / semantic_rejection: 53
- completed / evidence_sufficient: 9
- needs_clarification / None: 7
- partial / budget_exhausted: 6
- unsupported_method / unsupported_method: 1
- partial / invalid_task_output: 1
- failed / provider_failure: 1
- failed / budget_exhausted: 1
- failed / invalid_task_output: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 5, none 2 |
| comparison: decided/false | 6 | 1 | unable_to_decide/insufficient_evidence 5, decided/false 1 |
| comparison: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 5, none 2 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | unable_to_decide/insufficient_evidence 6, decided/false 1 |
| direct_fact: decided/false | 30 | 2 | unable_to_decide/insufficient_evidence 23, none 4, decided/false 2, unable_to_decide/conflicting_evidence 1 |
| direct_fact: decided/true | 16 | 5 | unable_to_decide/insufficient_evidence 10, decided/true 5, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 5 | unable_to_decide/insufficient_evidence 5, none 2 |

## Source check

- Cited statements: 40. Passage exists on the cited page with matching hashes: 40/40 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 21/40 (52%), partly 18/40 (45%), not supported 1/40 (2%).
- Labelled source: absent 50, same_site 13, same_page 10, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 46 (t-02, t-03, f-02, a-01, t-05, f-04, f-05, a-03, a-04, t-09, f-07, f-08, t-12, f-10, f-11, a-09, x-01, x-02, x-05, x-07, x-08, x-10, t-14, t-15, f-13, a-10, g-05, f-16, f-17, a-13, c-16, g-07, t-20, f-19, a-15, g-08, t-23, f-22, a-16, a-18, c-19, t-24, f-23, f-25, a-19, g-10)
- interpretation: 9 (f-01, g-01, g-02, a-06, c-07, u-04, u-07, t-21, f-20)
- passage reading: 7 (c-01, c-03, c-10, x-04, c-13, a-12, c-15)
- source selection: 5 (c-04, c-09, g-04, c-12, c-18)
- bad citations: 1 (f-14)

## Cost of a run

- Seconds per claim: median 54, max 126.
- Model calls per claim: mean 11.2; search calls: mean 5.2; pages extracted: mean 4.2.
- Tokens: 5,058,355 in runs that produced a result.
