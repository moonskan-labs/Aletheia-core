# Label audit for claims-20261115.csv (Nov 15, 2026)

Done before any scoring. No label in the CSV was changed; this file only lists findings
for the owner to accept or reject.

Method: the cited source page was fetched (Tavily extract) and read for all 20 Almost
claims and all 10 conflicting claims, plus 22 of the other 90 claims. The remaining 68
were read against their `source_shows` text only, without opening the page. 86 of the 90
distinct source URLs could be fetched.

## Summary

| result | count | claims |
|---|---|---|
| Wrong label | 1 | c-01 |
| Arguable label | 15 | a-03, a-04, a-05, a-13, a-17, f-16, x-01 to x-08, x-10 |
| Confirmed, source link broken | 1 | a-07 |
| Confirmed against the opened source | 35 | see below |
| Read only, source not opened | 68 | no problem seen |

## Wrong

- **c-01** (tuning, comparison, labelled false): "SI prefixes outnumber SI base units under
  the 2026 NIST listing." NIST lists 24 prefixes and seven base units, so the claim is
  **true**. Proposed label: decided / true.

## Arguable

- **a-03** (tuning): "TRACE and CONNECT both qualify as safe". Two equal halves, one true
  and one false. Almost or False are both defensible.
- **a-04** (tuning): "must support GET and POST" (really GET and HEAD). Same pattern.
- **a-13** (tuning): "Cardman and Ayers both rode Crew-11" (Ayers flew Crew-10). Same pattern.
- **a-05** (heldout): Convention "convened on May 25 and already had the quorum". The
  Archives page says it convened May 14 and got its quorum May 25, which supports Almost.
  Many histories say the Convention opened on May 25, which supports True.
- **a-17** (heldout): Article 29 "binds only half of each party's territory". The stated
  rule is invented and the core is wrong. Leans False, not Almost.
- **f-16** (tuning, labelled false): "Crew-11 carried three astronauts". NASA's page lists
  two NASA astronauts, one JAXA astronaut and one Roscosmos cosmonaut, so "three
  astronauts" can be read as literally true. False (four crew) is still the natural reading.
- **x-01 to x-08** (conflicting; x-03 and x-06 are heldout): both numbers were found in the
  cited sources, so the sources do differ. But every claim says "estimated" or "an
  estimate", and the World Bank figure is a real published estimate, so True is defensible.
  x-03 ("A population estimate for Canada ... was") and x-04 ("was estimated to have") lean
  True most clearly. The two sources also use different reference dates and definitions.
- **x-10** (tuning, conflicting): "A 2025 Oregon publication measured Mount Hood at 11,249
  feet." The claim is about what that publication says, and it does say 11,249. Leans True.

## Confirmed against the opened source

- Almost: a-01, a-02, a-06, a-08, a-09, a-10, a-11, a-12, a-14, a-15, a-16, a-18, a-19, a-20.
  a-14's own source page could not be fetched; another IOC page lists the same eight events.
- Almost, source link broken: **a-07**. The label is right (the proclamation exempts New
  Orleans) but the NPS PDF link now returns a "page not found" page. Proposed replacement:
  the National Archives transcript of the Emancipation Proclamation.
- Conflicting: x-09 (NPS gives 14,494 "under debate" on one page and 14,505 on another).
- Others: t-01, t-12, t-13, t-15, t-19, t-20, t-21, t-24, t-25, f-13, f-18, f-19, f-20,
  f-24, f-25, c-09, c-10, c-14, c-18, g-05, g-08.

## Notes for scoring

- Scores use the labels exactly as they are in the CSV. Where a miss falls on a claim listed
  above, the report says so instead of counting it as a pipeline fault without comment.
- The conflicting group stays out of the headline accuracy (already agreed).
- The 10 "causal" rows are plain facts or "most of" statements and are scored as direct facts.
- u-08 ("exactly 10,000 eggs" on February 7, 2026) could not be checked: the note says the
  IOC gives a daily figure, and if that figure is 10,000 the label may be arguable.
