# Batch report: nvidia/Nemotron-3_5-Lightning

- Revision 1a93f9f, 10 of 10 claims run.
- Labels are unreviewed AI proposals; a miss can be a label error.
- Verdict matches label (conflict group excluded): 1/10 (10%).
- Verdict matches label (all claims): 1/10 (10%).

## How runs ended

- partial / semantic_rejection: 6
- partial / invalid_task_output: 4

## By case type

| group | claims | match | answers given |
|---|---|---|---|
| comparison: decided/false | 1 | 0 | unable_to_decide/insufficient_evidence 1 |
| comparison: decided/true | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| direct_fact: decided/almost | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| direct_fact: decided/false | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| direct_fact: decided/true | 2 | 0 | unable_to_decide/insufficient_evidence 2 |
| insufficient: unable_to_decide/insufficient_evidence | 1 | 1 | unable_to_decide/insufficient_evidence 1 |

## Source check

- Cited statements: 0. Passage exists on the cited page with matching hashes: 0/0.
- Judge (deepseek-ai/DeepSeek-V4-Pro-0813): supported 0/0, partly 0/0, not supported 0/0.
- Labelled source: absent 6, same_site 2, same_page 2.
- Explanation against the labelled source: None 10.

## Stage at fault for each miss (rule-based first guess)

- conclusion: 4 (t001, t004, t011, t016)
- passage reading: 3 (t002, t006, t013)
- source selection: 2 (t005, t017)

## Cost of a run

- Seconds per claim: median 59, max 72.
- Model calls per claim: mean 13.9; search calls: mean 7.3; pages extracted: mean 5.6.
- Tokens: 842,523 in runs that produced a result.
