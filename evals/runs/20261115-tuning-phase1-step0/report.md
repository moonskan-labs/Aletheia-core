# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision 55bef79, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 16/73 (22%).
- Verdict matches label (all claims): 19/80 (24%).
- Excluding conflict and arguable labels: 16/69 (23%).
- Arguable labels, reported separately: 3/11 (27%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.

## How runs ended

- partial / semantic_rejection: 44
- completed / evidence_sufficient: 12
- needs_clarification / None: 11
- partial / invalid_task_output: 8
- partial / budget_exhausted: 4
- failed / invalid_task_output: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 1 | none 5, decided/true 1, unable_to_decide/insufficient_evidence 1 |
| comparison: decided/false | 6 | 0 | unable_to_decide/insufficient_evidence 4, unable_to_decide/conflicting_evidence 2 |
| comparison: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 5, none 2 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 3 | unable_to_decide/insufficient_evidence 4, unable_to_decide/conflicting_evidence 3 |
| direct_fact: decided/false | 30 | 0 | unable_to_decide/insufficient_evidence 16, unable_to_decide/conflicting_evidence 10, none 2, decided/true 2 |
| direct_fact: decided/true | 16 | 10 | decided/true 10, unable_to_decide/conflicting_evidence 4, unable_to_decide/insufficient_evidence 1, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 5 | unable_to_decide/insufficient_evidence 5, none 2 |

## Source check

- Cited statements: 40. Passage exists on the cited page with matching hashes: 40/40 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 17/40 (42%), partly 21/40 (52%), not supported 2/40 (5%).
- Labelled source: absent 53, same_site 11, same_page 9, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 41 (t-03, f-01, f-02, f-04, a-03, a-04, c-04, t-09, f-07, f-08, a-06, a-07, c-06, t-11, t-12, f-10, a-09, g-04, c-12, x-01, x-02, x-04, x-05, f-13, f-14, f-16, f-17, a-12, a-13, c-16, f-19, f-20, a-15, c-18, f-22, a-16, a-18, t-24, f-23, f-25, a-19)
- interpretation: 12 (a-01, c-01, g-01, u-02, c-03, f-11, g-05, g-07, u-07, t-21, g-08, g-10)
- passage reading: 6 (c-07, c-09, c-10, a-10, c-13, c-19)
- source selection: 2 (f-05, c-15)
- bad citations: 1 (t-08)

## Cost of a run

- Seconds per claim: median 59, max 148.
- Model calls per claim: mean 10.6; search calls: mean 5.3; pages extracted: mean 4.1.
- Tokens: 5,407,186 in runs that produced a result.
