# 200-claim sheet, Nov 17 (`claims-20261117-200.csv`)

A second, independent claim set for measuring the simple loop with live search (issue #33,
step 1). None of these claims appears in the other CSVs under `evals/claims/`.

| Expected answer | Count |
| --- | ---: |
| true | 89 |
| false | 81 |
| cannot settle (`unable_to_decide`) | 30 (29 insufficient evidence, 1 conflicting evidence) |

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
   *not* to contain the claimed figure. Two drafts failed this check because the figure turned
   out to be real: 88,966 spectators at the 2022 World Cup final, and 285,000 copies of the
   first IKEA catalogue. Both were dropped. The cannot-settle labels rest on "no public
   source found", which is weaker than a positive source; treat them with that caution.
4. 212 claims were drafted, 41 first failed (mostly pages that could not be fetched) and were
   pointed at another page and rechecked, 2 were dropped, and 10 true claims with the weakest
   check strings were removed to reach 200.

`claims-20261117-200-verification.csv` lists, per claim, the URL fetched, the strings it had
to contain or not contain, and the result. This string check confirms the source states the
deciding fact. It does not prove the claim's wording matches the source in every detail.

Sources are a mix of primary pages (NIST, NASA, UNESCO, national archives, UN, WHO, CDC, RFC
Editor, central banks, museums) and Wikipedia, which was used where the primary page could
not be fetched automatically.

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
