# PR 27 review follow-up, carried by PR 28

PR 27's three files were copied into PR 28 unchanged before this follow-up. Its
closure means the files and tasks have moved, not that the review is complete.
Original review: https://github.com/skanvish11/Aletheia-core/pull/27
(The full review remains available on PR 27.)

The current 77-claim scoring configuration is frozen for historical comparisons.
It is not evidence that Pari and csalive completed the proposed human review.
Do not overwrite historical labels, claims, inclusion decisions or saved results.
An approved revision should have a new dataset version and an explicit mapping.

## Preserved review checklist

| Task | State | Required evidence / completion criterion |
| --- | --- | --- |
| Describe this as a recheck, not established ground truth | Partly addressed | The comparison heading now says automated recheck. Legacy filenames and imports remain for reproducibility; any future rename must update consumers together. |
| Document the recheck's provenance | Pending | Record the actual model/agent, prompt, execution date and input identity. These details are not established by the committed CSVs; do not invent them. |
| Mark secondary-only sources | Pending | x-02, x-04, x-05, x-07 and x-08 relied on FRED when World Bank access failed, per the reviewer. Record that explicitly in a versioned annotation, or save a successful primary-source recheck. |
| Define and reproduce quote verification | Pending | Explain what “0 failed quote checks” meant. Save retrieved text, URL, fetch timestamp and hash, and verify each cited quotation. A later fetch cannot prove what a page said during the original recheck. Existing pipeline snapshots are not automatically snapshots of the recheck's cited pages. |
| Record machine-readable human decisions | Tracking added; decisions pending | `recheck-review-decisions.csv` contains all 16 flagged IDs, proposals and current scoring values. `decision`, `decided_by`, and `decided_at` remain blank until actual approval. |
| Converge evaluation formats | Pending | Map this annotation/decision record to `evals/schema` or explicitly version the extension; do not silently treat it as schema-valid claims. |
| Preserve the reason for cannot_settle | Pending | Distinguish insufficient evidence from conflicting evidence in a versioned reference annotation. All seven flagged u-* claims currently represent insufficient evidence. |
| Human spot-check of agreements | Pending | Pari and csalive proposed checking about 10 of the 71 agreements. Record the selected IDs, source checks, reviewers and decisions. No completed spot-check is claimed here. |
| Replace invalid conflict cases | Pending | Review x-01, x-02, x-04, x-05, x-07 and x-08 as True for the specific estimator's published figure. Add genuinely conflicting claims about the same fact, not different agencies' estimates. The current trusted set has no conflict examples. |
| Resolve ambiguous wording | Pending | Reviewer proposed rewording x-10, c-03 and t-09. The scoring configuration instead excludes them; reconcile this explicitly rather than treating exclusion as acceptance of the proposal. |
| Confirm the seven insufficient cases | Pending | u-01, u-02, u-04, u-05, u-07, u-08 and u-10 need the recorded human confirmation proposed in the review. |

## How to record a decision

The CSV's `existing_*` columns are a snapshot of the current scorer inputs, including
any historical `owner_decision` text. They are not newly asserted approvals. A human
reviewer fills the separate decision/by/date fields and links supporting evidence in
notes. Neither the scorer nor model prompts consume this tracking file. After review,
create a separately versioned benchmark; retain the original 77-claim reports.

PR 28 also reports the label-provenance caveat in its runbook. Closing PR 27 must link
here so the remaining work stays discoverable from both PRs.
