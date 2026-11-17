# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision 7c9d52f, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 27/73 (37%).
- Verdict matches label (all claims): 27/80 (34%).
- Excluding conflict and arguable labels: 25/69 (36%).
- Arguable labels, reported separately: 2/11 (18%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.

## How runs ended

- partial / semantic_rejection: 34
- completed / evidence_sufficient: 28
- needs_clarification / None: 8
- partial / invalid_task_output: 6
- partial / budget_exhausted: 3
- failed / provider_failure: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | none 3, unable_to_decide/insufficient_evidence 3, decided/false 1 |
| comparison: decided/false | 6 | 1 | unable_to_decide/insufficient_evidence 4, decided/false 1, none 1 |
| comparison: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 7 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | unable_to_decide/insufficient_evidence 4, decided/false 3 |
| direct_fact: decided/false | 30 | 13 | decided/false 13, unable_to_decide/insufficient_evidence 11, none 3, decided/true 2, unable_to_decide/conflicting_evidence 1 |
| direct_fact: decided/true | 16 | 7 | decided/true 7, unable_to_decide/insufficient_evidence 6, decided/false 2, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 6 | unable_to_decide/insufficient_evidence 6, none 1 |

## Source check

- Cited statements: 87. Passage exists on the cited page with matching hashes: 87/87 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 31/87 (36%), partly 51/87 (59%), not supported 5/87 (6%).
- Labelled source: absent 45, same_site 17, same_page 11, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 32 (t-03, a-01, c-01, t-06, f-04, a-04, c-03, c-04, g-02, t-09, a-06, f-11, a-09, g-04, x-04, x-05, x-07, x-08, t-15, f-13, c-13, t-17, f-17, a-12, c-16, t-20, f-20, a-16, a-18, f-23, a-19, g-10)
- passage reading: 12 (t-05, c-07, t-12, c-10, c-12, x-01, x-02, x-10, c-15, c-18, g-08, c-19)
- interpretation: 8 (g-01, c-09, g-05, f-16, g-07, t-21, f-19, u-08)
- bad citations: 2 (f-14, t-24)
- provider or limit: 1 (f-10)

## Cost of a run

- Seconds per claim: median 50, max 194.
- Model calls per claim: mean 10.3; search calls: mean 5.1; pages extracted: mean 3.9.
- Tokens: 4,609,157 in runs that produced a result.
