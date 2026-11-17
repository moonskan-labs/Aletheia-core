# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision bde7613, 80 of 80 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Phase 1 scoring: Almost labels count as False; c-01 is corrected to True.
- Verdict matches label (conflict group excluded): 23/73 (32%).
- Verdict matches label (all claims): 23/80 (29%).
- Excluding conflict and arguable labels: 21/69 (30%).
- Arguable labels, reported separately: 2/11 (18%) (a-03, a-04, x-01, x-02, x-04, x-05, x-07, x-08, x-10, f-16, a-13).
- Labelled-source agreement is not model-judged: dataset sources never enter prompts.
- One run is one sample: the 95% interval around the headline figure is 22% to 43%. A smaller difference between two runs is not evidence of a change.

## Where verdicts are lost (conflict group excluded)

The code decision is computed from the component findings before the final check.

| stage | claims | code decision matches label |
|---|---|---|
| No evidence read (question asked, failure or no source) | 11 | |
| Evidence read, code reached no decision | 31 | |
| Code reached True or False | 31 | 24 |
| ...published after the final check | 23 | 19 |
| ...withheld by the final check | 8 | 5 |

## How runs ended

- partial / semantic_rejection: 32
- completed / evidence_sufficient: 24
- needs_clarification / None: 11
- partial / budget_exhausted: 8
- partial / invalid_task_output: 5

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| causal: decided/true | 7 | 1 | none 3, unable_to_decide/insufficient_evidence 2, decided/false 1, decided/true 1 |
| comparison: decided/false | 6 | 0 | unable_to_decide/insufficient_evidence 4, unable_to_decide/conflicting_evidence 1, none 1 |
| comparison: decided/true | 7 | 0 | unable_to_decide/insufficient_evidence 5, none 2 |
| conflict: unable_to_decide/conflicting_evidence | 7 | 0 | unable_to_decide/insufficient_evidence 4, decided/false 2, decided/true 1 |
| direct_fact: decided/false | 30 | 11 | unable_to_decide/insufficient_evidence 15, decided/false 11, unable_to_decide/conflicting_evidence 2, none 2 |
| direct_fact: decided/true | 16 | 7 | decided/true 7, unable_to_decide/insufficient_evidence 5, decided/false 2, unable_to_decide/conflicting_evidence 1, none 1 |
| insufficient: unable_to_decide/insufficient_evidence | 7 | 4 | unable_to_decide/insufficient_evidence 4, none 2, decided/false 1 |

## Source check

- Cited statements: 80. Passage exists on the cited page with matching hashes: 80/80 (100%).
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 54/80 (68%), partly 21/80 (26%), not supported 5/80 (6%).
- Labelled source: absent 42, same_site 19, same_page 12, no_label_source 7.
- Explanation against the labelled source: None 80.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 32 (t-03, f-02, a-01, t-05, f-04, f-05, a-04, c-03, t-09, f-07, f-08, a-06, c-06, t-12, f-11, a-09, g-04, x-02, x-05, x-10, t-14, f-16, f-17, a-12, c-15, c-16, g-07, t-21, f-20, a-16, a-18, f-23)
- interpretation: 11 (c-01, u-01, u-05, t-15, c-13, g-05, f-19, c-18, g-08, f-22, g-10)
- passage reading: 11 (g-01, c-07, u-04, c-10, x-01, x-04, x-07, x-08, t-18, c-19, t-24)
- source selection: 3 (c-04, c-09, c-12)
- bad citations: 2 (t-11, f-10)

## Cost of a run

- Seconds per claim: median 48, max 123.
- Model calls per claim: mean 10.8; search calls: mean 5.0; pages extracted: mean 4.0.
- Tokens: 5,401,379 in runs that produced a result.
