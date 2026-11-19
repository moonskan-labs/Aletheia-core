# Provenance evaluation results

Packets: `packets.json` (sha256 `4cc25300a9d708e8…`), 3 repeats per case, model `deepseek-ai/DeepSeek-V4-Pro-0813`, max output tokens 16384, provider timeout 120 s.

- Before: commit `3c3e0aff83`, prompt `one-call-v1`
- After: prompt `one-call-v2`, run from a working tree on top of `a27362a013` holding this branch's fix (the run file records that commit)
- Stages: live model: verdict call, quotation checks, direction check; skipped: planning, search, page reads, follow-up round. Nothing is mocked.

A case's outcome is the majority over its repeats; the letters in brackets are the individual runs (T = True, F = False, I = Insufficient evidence, E = execution failure). The simple loop has no conflict or clarification outcome, so none appears.

## The two questions

| | Before | After |
| --- | --- | --- |
| Unsubstantiated claims (of 10) that received True | 9 | 0 |
| Supported claims (of 10) that correctly received True | 8 | 9 |
| Unsubstantiated: individual runs (of 30) that returned True | 25 | 0 |
| Supported: individual runs (of 30) that returned True | 24 | 26 |

## Who withheld the verdict (after)

Runs where the outcome was not True, split by whether the model itself declined or a code check withheld the model's True or False.

| Group | Model declined | Code withheld | Direction check withdrew | No usable quotation |
| --- | ---: | ---: | ---: | ---: |
| Supported | 0 | 2 | 0 | 2 |
| Unsubstantiated | 29 | 1 | 0 | 0 |

## All cases

S = supported (expected True), U = unsubstantiated (expected Insufficient), X = two extra cases reported outside the 20.

| Case | Problem | Claim | Expected | Before | After | Change | Decisive evidence or failure (after) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | measurement_original_record | In a continuous video-playback test, the Kestrel 7 tablet's battery lasted 20 hours. | True | Insufficient (I/T/I) | True (T/T/T) | fixed | original_record: www.voltreonlabs.com |
| U01 | anecdote_repeated | In a continuous video-playback test, the Pelora Note 5 tablet's battery lasted 22 hours. | Insufficient | True (I/T/T) | Insufficient (I/I/I) | fixed | The pages supply only an unsourced assertion by GearWire, a personal forum anecdote, and a secondhand summary  |
| S02 | attribution_publication | Corvane advertised the X2 tablet's battery life as up to 20 hours. | True | True (I/T/T) | True (T/T/I) | correct | original_record: www.corvane.com |
| U02 | announcement_paraphrased | In a continuous video-playback test, the Corvane X2 tablet's battery lasted 20 hours. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | Page 1 states the claimed test result but gives no tester, method, date, or test record, so it is not a docume |
| S03 | benchmark_original_record | The Arvo-3 language model scored 71.4% on the Lumen-QA benchmark. | True | True (T/T/T) | True (T/T/T) | correct | original_record: www.lumenqa.org |
| U03 | circular_citation | The Nimbra-2 language model scored 74.2% on the Lumen-QA benchmark. | Insufficient | True (T/I/T) | Insufficient (I/I/I) | fixed | All three pages merely repeat or cite one another's reporting of the score; none supplies a first-hand benchma |
| S04 | official_result | Ana Ferreira won the 2025 Harrowgate Marathon women's race in 2:24:31. | True | True (T/T/T) | True (T/T/T) | correct | original_record: www.harrowgatemarathon.org |
| U04 | repeated_unofficial_result | Tomas Lind won the 2025 Saltmere Marathon men's race in 2:09:47. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | The pages repeat the result as blog or news assertions, but none supplies an official race results or timing r |
| S05 | attribution_publication | The Orlen Valley Water Authority's 2025 annual report states that it treated 41.2 billion litres of water. | True | True (T/T/T) | True (T/T/T) | correct | original_record: www.orlenvalleywater.gov |
| U05 | attribution_without_record | The Merrow Basin Water Board's 2025 annual report states that it treated 38.6 billion litres of water. | Insufficient | Insufficient (I/I/I) | Insufficient (I/I/I) | correct | No supplied page mentions the 2025 annual report or shows it. Page 2 attributes the figure to a spokesperson r |
| S06 | attribution_publication_real | Denali, the highest point in Alaska, has an elevation of 20,320 feet, according to the U.S. Geological Survey. | True | Insufficient (I/I/I) | Insufficient (I/T/I) | still wrong | No usable supporting quotation was returned. |
| U06 | anecdote_misattributed | Mount Arvid, the highest point in Tessaly County, has an elevation of 8,214 feet, according to the Tessaly County Survey Office. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | Page 1 states all parts of the claim but only as a secondhand attribution to the Tessaly County Survey Office, |
| S07 | attribution_publication_real | The World Health Organization estimated that 610,000 people died of malaria worldwide in 2024. | True | True (T/T/T) | True (T/T/T) | correct | original_record: www.who.int |
| U07 | unknown_origin | The Ostrava Institute for Tropical Health estimated that 47,000 people died of dengue worldwide in 2024. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | Both supplied pages are secondhand reports attributing the 47,000 figure to the Ostrava Institute, but neither |
| S08 | official_record_real | NASA's SpaceX Crew-11 mission launched from Launch Complex 39A at Kennedy Space Center at 11:43 a.m. EDT. | True | True (T/T/T) | True (I/T/T) | correct | original_record: www.nasa.gov |
| U08 | bare_assertion | The Halcyon-4 crewed mission launched from Pad 2 at Varnholm Spaceport at 9:17 a.m. local time. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | Page 1 states the exact location and time, but it offers no underlying record, producer, or date; it is an uns |
| S09 | owner_record | Biscuit, the mascot dog of Ashcombe Town Football Club, is a golden retriever. | True | True (T/T/T) | True (T/T/T) | correct | original_record: www.ashcombetownfc.co.uk |
| U09 | planted_mentions | Pebble, the mascot dog of Fenwick Rangers Football Club, has a blue coat. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | All three pages state the description, but only as a personal anecdote, an unsourced fact list, and a fan note |
| S10 | measurement_original_record | Ternwell Audio Lab measured the Quill E4 earbuds' battery life at 9.5 hours. | True | True (T/T/T) | True (T/T/T) | correct | original_record: www.ternwellaudiolab.com |
| U10 | fabricated_record | Lumora Labs measured the Vexa S2 earbuds' battery life at 11 hours. | Insufficient | True (T/T/T) | Insufficient (I/I/I) | fixed | Every supplied page states the claimed result, but none is Lumora Labs' own publication. All three pages are t |
| X01 | conditions_mismatch | In a continuous web-browsing test, the Kestrel 7 tablet's battery lasted 20 hours. | Insufficient | False (F/F/F) | False (F/F/F) | still wrong | original_record: www.voltreonlabs.com |
| X02 | contradicted_by_record | In a continuous video-playback test, the Kestrel 7 tablet's battery lasted 24 hours. | False | False (F/F/F) | False (F/F/F) | correct | original_record: www.voltreonlabs.com |
