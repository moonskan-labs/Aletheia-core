# 200-claim sheet, Nov 17 (`claims-20261117-200.csv`)

A second, independent claim set for measuring the simple loop with live search (issue #33,
step 1). None of these claims appears in the other CSVs under `evals/claims/`.

| Expected answer | Count |
| --- | ---: |
| true | 90 |
| false | 82 |
| cannot settle (`unable_to_decide`) | 28 (27 insufficient evidence, 1 conflicting evidence) |

These counts include two labels corrected after the first live run (see "Corrections" below).

Subjects: science 27, history 27, geography 23, technology 20, sports records 19, law and
treaties 18, arts and culture 17, space 14, economics and statistics 12, public health 12,
business 11. Every row is `split=heldout`: none of these claims was used to tune anything.

Same 17 columns as `claims-20261115.csv`; the file loads through
`aletheia.evaluation.load_claims_csv`. IDs are `s200-001` to `s200-200`, in shuffled order.

## How the labels were made

**The claims and labels were written by Claude (an AI assistant), not by a person.** Each
label was then checked against one fetched source page:

1. Each claim was written with a source URL, what that source shows, and one or more short
   strings that decide the claim. For a true claim, that's the claimed value; for a false
   claim, the correct value the claim contradicts.
2. Every source page was fetched on 2026-11-17 through Tavily extract, falling back to a
   direct fetch. The claim was kept only if the page contained the deciding string(s).
3. **Cannot-settle claims** state a precise figure that no public record holds (for example,
   an exact attendance count on one day). For these, the related source page was checked
   *not* to contain the claimed figure. These labels rest on "no public source found",
   which is weaker than a positive source; treat them with that caution. Figures that turn
   out to be real are the main risk: 88,966 (spectators at the 2022 World Cup final) and a
   15 cc first insulin dose were removed on review before checking, and 285,000 (copies of
   the first IKEA catalogue) was removed because the check found it on the page.
4. 214 claims were drafted. 2 were removed on review (above). Of the remaining 212, 171
   passed the first check. The 41 that failed were almost all pages that could not be
   fetched, or wording that differed from the check string; none showed a wrong label. They
   were pointed at another page and rechecked. Two were dropped: the IKEA claim, and
   tungsten's melting point, which had no clean check string. Finally, the 10 true claims
   with the weakest check strings were removed to reach 200.

`claims-20261117-200-verification.csv` lists, per claim, the URL fetched, the strings it had
to contain or not contain, and the result. This string check confirms the source states the
deciding fact. It does not prove the claim's wording matches the source in every detail.

Sources are a mix of primary pages (NIST, NASA, UNESCO, national archives, UN, WHO, CDC, RFC
Editor, central banks, museums) and Wikipedia, which was used where the primary page could
not be fetched automatically.

## Corrections after the first live run

Reviewing the misses of the first live run (`evals/runs/20261117-s200-live-gptoss120-a`) showed
that two cannot-settle labels were wrong. The model had found the evidence, so both were
relabelled, and each row's `note` says so:

- `s200-108` (Bolt took exactly 41 strides in the 9.58 s run): **true**. A peer-reviewed
  biomechanics review (PMC10669785) reports 41 steps.
- `s200-009` (exactly 1,212 workers on the Eiffel Tower site on completion day): **false**.
  The official Tour Eiffel history gives 150 to 300 workers on site.

The check in step 3 only confirmed that the claimed figure was absent. It could not catch a
figure that is documented elsewhere, or a range on the page that rules it out. Three more
cannot-settle labels are debatable, and were left unchanged: `s200-135`, `s200-147` and
`s200-175` (see the run's `diagnosis.csv`). No other label was changed. Every run's own
`labels.json` and `scores.json` keep the labels as they were when that run started;
`scripts/score_sheet.py` scores against the current CSV.

## What the model sees

Only the `claim` text. `BatchClaim.request()` sends `{"claim": ...}` and nothing else; the
source URL, expected answer and notes stay in the scoring process. No claim text contains a
URL (checked when the file was built). The agent finds its own pages through live search;
if it happens to reach the same page used for labelling, it found it itself.

## Known limits

- Mostly well-known, stable facts (162 of 200 are `direct_fact`), so this set is probably
  easier than the 77 trusted tuning claims, which are anchored to 2025–2026 events and exact
  statistics. Compare across sets with that in mind.
- Single source per claim; no second reviewer.
