# Batch report: Qwen/Qwen3-235B-A22B-Instruct-2507

- Revision eda33c7, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 43/73 (59%).
- Verdict matches label (all claims): 43/80 (54%).
- Excluding conflict and arguable labels: 41/69 (59%).
- Arguable labels, reported separately: 2/11 (18%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.
- One run is one sample: the 95% interval around the headline figure is 47% to 69%. A smaller difference between two runs is not evidence of a change.

## Where verdicts are lost (conflict group excluded)

The code decision is computed from the component findings before the final check.

| stage | claims | code decision matches label |
|---|---|---|
| No evidence read (question asked, failure or no source) | 4 | |
| Evidence read, code reached no decision | 21 | |
| Code reached True or False | 48 | 44 |
| ...published after the final check | 41 | 37 |
| ...withheld by the final check | 7 | 7 |

## How runs ended

- completed / evidence_sufficient: 44
- partial / semantic_rejection: 25
- partial / invalid_task_output: 3
- failed / invalid_task_output: 3
- partial / budget_exhausted: 3
- completed / no_useful_query: 1
- unsupported_method / unsupported_method: 1

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 5, decided/false 1, unable_to_decide/conflicting_evidence 1 |
| comparison: decided/false | 6 | 3 | decided/false 3, unable_to_decide/insufficient_evidence 3 |
| comparison: decided/true | 7 | 1 | unable_to_decide/insufficient_evidence 6, decided/true 1 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | decided/false 5, unable_to_decide/insufficient_evidence 2 |
| direct_fact: decided/false | 30 | 25 | decided/false 25, none 2, unable_to_decide/insufficient_evidence 1, unable_to_decide/conflicting_evidence 1, decided/true 1 |
| direct_fact: decided/true | 16 | 8 | decided/true 8, unable_to_decide/insufficient_evidence 4, decided/false 2, unable_to_decide/conflicting_evidence 1, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 6 | unable_to_decide/insufficient_evidence 6, none 1 |

## Source check

- Cited statements: 157. Passage exists on the cited page with matching hashes: 157/157 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 97/157 (62%), partly 49/157 (31%), not supported 11/157 (7%).
- Labelled source: absent 46, same_site 20, no_label_source 7, same_page 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 19 (t-02, c-01, g-01, a-03, g-02, t-09, f-07, a-06, c-06, t-12, c-10, x-02, x-10, t-14, g-05, t-18, c-15, g-07, g-10)
- passage reading: 11 (c-07, g-04, x-01, x-04, x-05, x-07, x-08, t-15, c-13, t-17, c-19)
- bad citations: 4 (f-08, t-11, f-16, t-24)
- provider or limit: 3 (f-05, a-04, t-21)
- source selection: 3 (c-12, c-16, g-08)
- interpretation: 1 (u-08)

## Cost of a run

- Seconds per claim: median 59, max 199.
- Model calls per claim: mean 9.3; search calls: mean 4.7; pages extracted: mean 3.8.
- Tokens: 3,989,411 in runs that produced a result.
