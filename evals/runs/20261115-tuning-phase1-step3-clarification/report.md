# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision f1e9a38, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 29/73 (40%).
- Verdict matches label (all claims): 29/80 (36%).
- Excluding conflict and arguable labels: 28/69 (41%).
- Arguable labels, reported separately: 1/11 (9%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.

## How runs ended

- partial / semantic_rejection: 34
- completed / evidence_sufficient: 22
- needs_clarification / None: 10
- partial / invalid_task_output: 6
- partial / budget_exhausted: 5
- failed / budget_exhausted: 2
- unsupported_method / unsupported_method: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | none 4, unable_to_decide/insufficient_evidence 2, decided/false 1 |
| comparison: decided/false | 6 | 2 | unable_to_decide/insufficient_evidence 4, decided/false 2 |
| comparison: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 6, none 1 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | unable_to_decide/insufficient_evidence 7 |
| direct_fact: decided/false | 30 | 14 | decided/false 14, unable_to_decide/insufficient_evidence 9, none 6, decided/true 1 |
| direct_fact: decided/true | 16 | 7 | decided/true 7, unable_to_decide/insufficient_evidence 6, unable_to_decide/conflicting_evidence 1, decided/false 1, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 6 | unable_to_decide/insufficient_evidence 6, none 1 |

## Source check

- Cited statements: 67. Passage exists on the cited page with matching hashes: 67/67 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 36/67 (54%), partly 25/67 (37%), not supported 6/67 (9%).
- Labelled source: absent 47, same_site 18, same_page 8, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 30 (t-03, c-01, f-05, a-04, g-02, t-09, f-08, a-06, t-11, t-12, a-09, g-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, t-14, t-18, f-16, f-17, a-12, c-15, c-16, a-16, c-19, t-24, f-23)
- interpretation: 11 (f-11, u-05, g-05, a-13, g-07, t-21, f-19, f-20, g-08, f-22, g-10)
- passage reading: 5 (g-01, c-03, c-07, c-10, t-15)
- bad citations: 4 (a-03, c-04, f-07, f-25)
- source selection: 3 (c-09, c-12, c-18)
- provider or limit: 2 (c-13, a-19)

## Cost of a run

- Seconds per claim: median 39, max 129.
- Model calls per claim: mean 10.1; search calls: mean 4.7; pages extracted: mean 3.7.
- Tokens: 4,221,983 in runs that produced a result.
