# 200 evaluation claims — November 16, 2026

[CSV dataset](claims-20261116-200.csv)

These are **accepted evaluation labels**, adopted at the user's direction. They were authored by AI using the cited sources; acceptance does not imply independent human verification or blind reconciliation. The user's instruction overrides the human-review prerequisite for using this CSV set. The file uses the same 17 columns as the November 15 CSV and loads through `load_claims_csv`. Each row includes an expected decision, a reference URL, evidence notes, and a provenance note. All 20 Almost rows include the three correction fields.

## Composition

| Expected decision | Count |
| --- | ---: |
| True | 80 |
| False | 80 |
| Almost | 20 |
| Unable to decide: insufficient evidence | 20 |
| Total | 200 |

| Domain | Count |
| --- | ---: |
| Astronomy | 50 |
| Technology | 50 |
| Biology | 30 |
| Earth science | 30 |
| History | 30 |
| Arts | 10 |

Case types: 153 direct facts, 18 comparisons, 9 causal claims, and 20 insufficient-evidence claims. No conflicting-evidence cases were manufactured to satisfy a quota. This set does not measure that category or qualification-flag accuracy.

## Split and independence

All 200 rows are `tuning`, following the independent held-out policy in [the evaluation guide](../README.md#held-out-policy). These author-visible claims cannot satisfy that policy. The existing November 15 set and `evals/claims.json` remain unchanged.

There are 20 source groups with 10 claims each. Rows were shuffled with seed `20261116` before assigning neutral IDs `n26-001` through `n26-200`. Keep these IDs stable when making corrections. Each row's `note` identifies its source group. Related claims share facts and are correlated; do not describe them as 200 independent research topics. If a separate evaluation partition is later authorized, partition entire source groups rather than individual rows.

Normalized claim text and IDs were checked against the November 15 CSV, the earlier 20-claim proposal, and the pilot handoff set. No exact normalized duplicates were found. This does not establish semantic independence.

## Evidence and provenance

Reference pages were retrieved and read on November 16, 2026, using primary sources: NASA, IETF/RFC Editor, NHGRI, USGS, NPS, National Archives, the Louvre, Library of Congress, and an additional Salk research summary for the RNA-origin hypothesis. Historical standards are scoped to their named RFC; their original limits should not be treated as descriptions of every modern extension. Broken museum and USGS links were replaced or omitted.

The 180 decided claims were labeled against those sources. This was an author check, not independent labeling. Many False cases intentionally alter a source fact; the reference supports the correction or contradiction, not the false statement itself. Almost labels treat the changed detail as secondary rather than materially changing the assertion; that distinction can be revisited in a later audit. Dates, names, and terminology dominate these corrections, limiting their diversity.

The 20 insufficient-evidence labels cover abstention probes: unresolved scientific hypotheses, undisclosed implementations or observations, future outcomes, and unrecorded historical details. Their sources often supply background rather than directly establish uncertainty. Missing information on one page is **not** evidence that a claim is false or unknowable. New direct evidence can justify revising these labels. These deliberately underspecified or exact-prediction cases are not representative of all real-world uncertainty.

Use these labels as the expected answers for this CSV evaluation set. Preserve the original IDs and record any later corrections. The separate `evals/claims.json` reconciliation format is unchanged; no labeler identities or blind human agreement are claimed.

## Runner behavior and checks

The current phase-one runner maps `almost` to **false** when scoring the complete statement as written (`BatchClaim.expected`). The original labels and corrections remain in the CSV. Its effective label mix is therefore 80 True, 100 False, and 20 insufficient-evidence cases. It sends only `claim` to the application; reference sources, notes, and expected answers stay evaluator-side.

Checks cover the 200-row count, unique IDs and normalized statements, compatibility with the actual CSV loader, decision consistency, required correction fields, reference fields, date, and the request-field allowlist. These structural checks do not prove label correctness. No application research runs or model evaluations were launched while creating this set.
