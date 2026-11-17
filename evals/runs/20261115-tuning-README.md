# 80 tuning claims on nvidia/Nemotron-3_5-Lightning, Nov 15, 2026

Three full runs of the same 80 tuning claims, one per code state. Every run is kept in the
folders beside this file (`report.md`, `report.csv`, one JSON per claim, source checks).
Nothing was rerun to get a better number. Judge for the source check:
deepseek-ai/DeepSeek-V4-Pro-0813. Labels are the unreviewed ones in the CSV; see
`evals/claims/claims-20261115-audit.md`. The heldout claims were not run.

| | before (b0e838e) | after fix 1 (f5ccdf1) | after fix 2 (be71eb3) |
|---|---|---|---|
| Verdict matches label, conflict group excluded | 6 of 73 (8%) | 4 of 73 (5%) | 16 of 73 (22%) |
| Verdict matches label, all 80 | 6 | 8 | 17 |
| Runs that published a verdict | 1 | 0 | 13 |
| Published verdicts that match the label | 1 | 0 | 10 |
| Runs that reached a preliminary True or False | 13 | 23 | 28 |
| Passage assessments recorded as a usable contradiction | 2 of 558 | 148 of 643 | 127 of 581 |
| Passage assessments recorded as "context" | 386 of 558 | 237 of 643 | 252 of 581 |
| Cited statements checked | 5 | 6 | 44 |
| Cited passage exists on the cited page, hashes match | 5 of 5 | 6 of 6 | 44 of 44 |
| Judge: supported / partly / not supported | 5 / 0 / 0 | 2 / 3 / 1 | 13 / 28 / 3 |
| Median seconds per claim | 68 | 69 | 64 |

Before the fixes, 5 of the 6 matches were "insufficient evidence" claims, which match
simply because the pipeline decided nothing.

## Fix 1: passage reading (most common cause in the baseline)

55 of 80 baseline runs never reached a preliminary verdict. The model filed passages as
"context" even when its own note said the passage confirmed or contradicted the claim; only
2 of 558 assessments were usable contradictions, so no False claim could be decided. The
relation label was generated before the rationale. Now the rationale comes first and the
relation and scope fields carry short definitions. Effect on its own: usable contradictions
2 to 148, preliminary verdicts 13 to 23, but no gain in published verdicts, because the
final step then discarded all 23.

## Fix 2: final step (most common cause after fix 1)

The final check has an optional yes/no field that the model usually left out, and a missing
answer was treated as a rejection (28 of 111 rejected checks failed on that alone). The
model also kept proposing an "Almost" correction for plainly true claims, and a bad
proposal cancelled the whole verdict. Now the field is required, and a bad or ineligible
correction is dropped while the checked verdict is kept. Effect: published verdicts 0 to 13.

## Of the 13 published verdicts after fix 2

- 9 True verdicts match the label, and 1 Almost matches (a-18).
- c-01 was answered True against a False label; the audit found that label wrong, so the
  answer is right.
- x-07 was answered True against a "conflicting" label that the audit lists as arguable.
- f-02 was answered Almost against a False label. This one is a real error.

## Top three causes still open, with a proposed fix each

1. **No False verdict is ever published (15 of 16 preliminary False verdicts withheld).**
   The final check asks "decision_supported" and the model answers no because the *claim*
   is not supported, and lists the wrong components as "rejected". Proposed: ask the check
   one plain question per decision ("the evidence shows the claim is false: yes or no") and
   drop the rejected-components list for a False decision.
2. **One stray assessment makes a component "conflicting" (21 runs).** A single opposite
   label among eight, or overlapping fragment components (the whole sentence plus "$28.703
   billion" plus "Cupertino, California"), is enough to withhold the verdict. Proposed, in
   code: drop components whose text is contained in another component, and treat a
   conflict as real only when both sides have evidence that meets the evidence rule. The
   second part changes the evidence policy, so it needs the owner's yes.
3. **Comparisons and clarification (about 20 runs).** 9 runs stopped to ask a clarifying
   question on clear claims (mostly comparisons and "worldwide" wording), and comparisons
   that ran rarely extracted both numbers. Proposed: do not ask for clarification when the
   claim names both things being compared, and let a comparison use two separately cited
   plain facts when the operand fields do not validate.

Also seen: the judge rates 28 of 44 cited statements only "partly supported". The passages
are real and on the right page, but explanation sentences bundle more facts than the cited
passage states.
