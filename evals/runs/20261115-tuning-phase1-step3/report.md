# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision 400d0f6, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 23/73 (32%).
- Verdict matches label (all claims): 23/80 (29%).
- Excluding conflict and arguable labels: 23/69 (33%).
- Arguable labels, reported separately: 0/11 (0%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.

## How runs ended

- partial / semantic_rejection: 39
- completed / evidence_sufficient: 22
- needs_clarification / None: 8
- partial / budget_exhausted: 8
- failed / invalid_task_output: 2
- partial / invalid_task_output: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 1 | unable_to_decide/insufficient_evidence 3, none 2, decided/true 1, unable_to_decide/conflicting_evidence 1 |
| comparison: decided/false | 6 | 0 | unable_to_decide/insufficient_evidence 5, none 1 |
| comparison: decided/true | 7 | 2 | unable_to_decide/insufficient_evidence 5, decided/true 2 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | unable_to_decide/insufficient_evidence 5, decided/false 2 |
| direct_fact: decided/false | 30 | 6 | unable_to_decide/insufficient_evidence 16, decided/false 6, none 4, decided/true 2, unable_to_decide/conflicting_evidence 2 |
| direct_fact: decided/true | 16 | 9 | decided/true 9, unable_to_decide/insufficient_evidence 5, unable_to_decide/conflicting_evidence 1, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 5 | unable_to_decide/insufficient_evidence 5, none 2 |

## Source check

- Cited statements: 65. Passage exists on the cited page with matching hashes: 65/65 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 31/65 (48%), partly 28/65 (43%), not supported 6/65 (9%).
- Labelled source: absent 49, same_site 15, same_page 9, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 40 (f-01, a-01, t-05, f-05, a-03, a-04, g-02, f-07, f-08, a-06, a-07, c-06, t-12, f-10, f-11, a-09, c-09, g-04, c-12, x-01, x-05, x-07, x-08, x-10, t-14, t-15, a-10, f-16, a-12, c-16, g-07, t-20, f-20, a-15, a-16, a-18, c-19, t-24, a-19, g-10)
- interpretation: 9 (u-02, c-04, a-13, t-21, f-19, g-08, u-08, f-22, f-23)
- passage reading: 5 (c-01, c-10, x-02, x-04, c-13)
- bad citations: 3 (t-06, f-04, f-25)
- source selection: 2 (c-03, c-18)
- planning: 1 (g-01)

## Cost of a run

- Seconds per claim: median 51, max 110.
- Model calls per claim: mean 10.7; search calls: mean 5.0; pages extracted: mean 4.0.
- Tokens: 5,027,797 in runs that produced a result.
