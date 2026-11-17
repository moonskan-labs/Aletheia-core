# Ground-truth review

| Count | Claims |
| --- | ---: |
| agree | 71 |
| differ | 9 |
| ambiguous | 3 |
| cannot_settle | 7 |
| failed quote check | 0 |

Agree and differ compare the normalized old label with the new verdict across all 80 tuning claims. Ambiguous, cannot_settle, and failed quote check are overlapping counts of the new results. The c-01 correction is applied before comparison.

Failed quote check IDs: None.

## u-01

**Claim**

```text
Exactly 1,842 people sat in the audience for the 2025 Nobel Physics lecture in Stockholm, Sweden.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched Nobel Foundation annual report and lecture-attendance searches; neither reported an exact in-person count.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.kva.se/en/event/the-nobel-lectures-2025-2/
```

**New quote**

```text
Address: Aula Magna, Stockholm University
```

**New wrong_detail**

```text

```

**New note**

```text
The organizer's opened programme describes registration and venue but gives no attendance count. Targeted searches did not locate a record confirming or contradicting exactly 1,842 attendees; Nobel.org pages returned 403.
```

Owner decision:


## u-02

**Claim**

```text
Online viewers submitted precisely 3,117 questions to the 2025 Nobel Chemistry lecture in Stockholm, Sweden.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched the Nobel Foundation report and targeted lecture-question searches; no reliable exact total appeared.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.kva.se/en/event/the-nobel-lectures-2025-2/
```

**New quote**

```text
Live-streamed and available on demand
```

**New wrong_detail**

```text

```

**New note**

```text
The organizer's opened programme provides no count of questions submitted by online viewers. Targeted searches did not establish or contradict 3,117; Nobel.org pages returned 403.
```

Owner decision:


## c-03

**Claim**

```text
For the same nonempty resource, a 200 GET response carries more body bytes than a 200 HEAD response under the 2022 HTTP standard worldwide.
```

**Review reason:** verdicts differ; new verdict is ambiguous.

**Old label:** true

**Original expected_verdict:** true

**Original expected_outcome:** decided

**Old source_url_1**

```text
https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/GET
```

**Old source_shows_1**

```text
MDN explains that GET requests retrieve a representation of the target.
```

**New verdict:** ambiguous

**New source_url**

```text
https://www.rfc-editor.org/rfc/rfc9110.html
```

**New quote**

```text
The HEAD method is identical to GET except that the server MUST NOT send content in the response.
```

**New wrong_detail**

```text

```

**New note**

```text
True on the ordinary reading that the 200 GET transfers a nonempty representation: positive bytes exceed HEAD's zero. False as a universal requirement for any nonempty resource: section 15.3.1 allows explicitly zero-length 200 content, and a resource is distinct from its selected representation.
```

Owner decision:


## t-09

**Claim**

```text
The First Congress sent 12 proposed constitutional amendments from New York to the states on September 25, 1789.
```

**Review reason:** verdicts differ; new verdict is ambiguous.

**Old label:** true

**Original expected_verdict:** true

**Original expected_outcome:** decided

**Old source_url_1**

```text
https://www.archives.gov/milestone-documents/bill-of-rights
```

**Old source_shows_1**

```text
The Archives gives the 1789 proposal of 12 amendments and later compensation-amendment ratification.
```

**New verdict:** ambiguous

**New source_url**

```text
https://www.archives.gov/milestone-documents/bill-of-rights
```

**New quote**

```text
On September 25, 1789, the First Congress of the United States therefore proposed to the state legislatures 12 amendments to the Constitution that met arguments most frequently advanced against it.
```

**New wrong_detail**

```text

```

**New note**

```text
True if 'sent' means Congress formally proposed the 12 amendments for state ratification on September 25. False if it means actual dispatch to the states: Washington sent the copies on October 2. Congress sat in New York; the ambiguity concerns proposal versus transmission.
```

Owner decision:


## u-04

**Claim**

```text
Outside Independence Hall in Philadelphia, Pennsylvania, 2,417 spectators watched the September 17, 1787, Constitution signing.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched National Archives and National Park Service accounts of the signing; no reliable spectator count was reported.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.nps.gov/articles/000/constitutionalconvention-september17.htm
```

**New quote**

```text
After the signing, the Convention adjourned for a final time.
```

**New wrong_detail**

```text

```

**New note**

```text
The opened NPS day-by-day account and National Archives account identify the signing but do not report 2,417 spectators outside. Targeted search found no attendance record. No inferred falsity from absence.
```

Owner decision:


## u-05

**Claim**

```text
Exactly 87 hikers reached Mount Whitney’s California summit on July 1, 2001.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched USGS historical elevation material and date-specific summit logs; no reliable exact daily count was found.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.nps.gov/seki/planyourvisit/whitney.htm
```

**New quote**

```text
All hikers entering the Mt. Whitney zone, including day-hikers, are required to obtain a permit.
```

**New wrong_detail**

```text

```

**New note**

```text
The opened NPS page explains permits but contains no summit-arrival count for July 1, 2001. Targeted search found no register establishing or contradicting exactly 87; permits would not establish actual summit arrivals.
```

Owner decision:


## x-01

**Claim**

```text
The United States had 340,003,797 people in its estimated midyear 2024 population.
```

**Review reason:** verdicts differ.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://fred.stlouisfed.org/data/POPTOTUSA647NWDB
```

**Old source_shows_1**

```text
FRED republishes the World Bank population series with a 2024 value of 340,003,797 people for United States.
```

**New verdict:** true

**New source_url**

```text
https://www.census.gov/newsroom/press-releases/2026/2025-popest-metro-micro-counties.html
```

**New quote**

```text
United States
336,755,052
340,003,797
341,784,857
```

**New wrong_detail**

```text

```

**New note**

```text
Census Vintage 2025 estimates, available before the as_of date.
```

Owner decision:


## x-02

**Claim**

```text
China’s July 2024 population estimate stood at 1,408,975,000 people.
```

**Review reason:** verdicts differ.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://fred.stlouisfed.org/data/POPTOTCNA647NWDB
```

**Old source_shows_1**

```text
FRED republishes the World Bank population series with a 2024 value of 1,408,975,000 people for China.
```

**New verdict:** true

**New source_url**

```text
https://fred.stlouisfed.org/series/POPTOTCNA647NWDB
```

**New quote**

```text
2024:
1,408,975,000
```

**New wrong_detail**

```text

```

**New note**

```text
Secondary republication only: FRED's World Bank WDI series. World Bank page opened but its values were not exposed; direct API timed out. Midyear interpreted as July estimate.
```

Owner decision:


## x-04

**Claim**

```text
At midyear 2024, Australia was estimated to have 27,194,286 residents.
```

**Review reason:** verdicts differ.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://fred.stlouisfed.org/data/POPTOTAUA647NWDB
```

**Old source_shows_1**

```text
FRED republishes the World Bank population series with a 2024 value of 27,194,286 people for Australia.
```

**New verdict:** true

**New source_url**

```text
https://fred.stlouisfed.org/series/POPTOTAUA647NWDB
```

**New quote**

```text
2024:
27,194,286
```

**New wrong_detail**

```text

```

**New note**

```text
Secondary republication only: FRED's World Bank WDI series, updated July 7, 2026. World Bank page was rate limited and direct API timed out.
```

Owner decision:


## x-05

**Claim**

```text
Japan counted an estimated 123,975,371 people at the midpoint of 2024.
```

**Review reason:** verdicts differ.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://fred.stlouisfed.org/data/POPTOTJPA647NWDB
```

**Old source_shows_1**

```text
FRED republishes the World Bank population series with a 2024 value of 123,975,371 people for Japan.
```

**New verdict:** true

**New source_url**

```text
https://fred.stlouisfed.org/series/POPTOTJPA647NWDB
```

**New quote**

```text
2024:
123,975,371
```

**New wrong_detail**

```text

```

**New note**

```text
Secondary republication only: FRED's World Bank WDI series. Direct World Bank pages failed or exposed no numerical observations; API retrieval timed out. Midyear interpreted as July 1.
```

Owner decision:


## x-07

**Claim**

```text
An estimated 5,290,000 people lived in New Zealand at midyear 2024.
```

**Review reason:** verdicts differ.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://fred.stlouisfed.org/data/POPTOTNZA647NWDB
```

**Old source_shows_1**

```text
FRED republishes the World Bank population series with a 2024 value of 5,290,000 people for New Zealand.
```

**New verdict:** true

**New source_url**

```text
https://fred.stlouisfed.org/series/POPTOTNZA647NWDB
```

**New quote**

```text
2024:
5,290,000
```

**New wrong_detail**

```text

```

**New note**

```text
Secondary republication only: FRED's World Bank WDI series. Direct World Bank pages failed or exposed no numerical observations; API retrieval timed out. Midyear interpreted as July 1.
```

Owner decision:


## x-08

**Claim**

```text
Sweden’s estimated population on July 1, 2024, was 10,569,709 people.
```

**Review reason:** verdicts differ.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://fred.stlouisfed.org/data/POPTOTSEA647NWDB
```

**Old source_shows_1**

```text
FRED republishes the World Bank population series with a 2024 value of 10,569,709 people for Sweden.
```

**New verdict:** true

**New source_url**

```text
https://fred.stlouisfed.org/series/POPTOTSEA647NWDB
```

**New quote**

```text
2024:
10,569,709
```

**New wrong_detail**

```text

```

**New note**

```text
Secondary republication only: FRED's World Bank WDI series. Direct World Bank pages failed or exposed no numerical observations; API retrieval timed out. Midyear interpreted as July 1.
```

Owner decision:


## x-10

**Claim**

```text
A 2025 Oregon publication measured Mount Hood in Oregon at 11,249 feet above sea level.
```

**Review reason:** verdicts differ; new verdict is ambiguous.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text
https://www.oregon.gov/osbeels/Documents/OregonExaminer/2025Examiner-Winter.pdf
```

**Old source_shows_1**

```text
Oregon’s 2025 surveying bulletin identifies Mount Hood as in Oregon and gives its summit as 11,249 feet.
```

**New verdict:** ambiguous

**New source_url**

```text
https://www.oregon.gov/osbeels/Documents/OregonExaminer/2025Examiner-Winter.pdf
```

**New quote**

```text
With a summit elevation of 11,249
ft (3,429 m), it is the highest mountain in the U.S. state of Oregon
```

**New wrong_detail**

```text

```

**New note**

```text
True if 'measured ... at' means the elevation reported in the Winter 2025 Oregon Examiner: it states 11,249 ft. Cannot settle if it asserts that this publication conducted an actual measurement or new survey: it merely captions Mount Hood and supplies no measurement method or survey date.
```

Owner decision:


## u-07

**Claim**

```text
Exactly 6,324 visitors watched the September 24, 2025, IMAP launch from Kennedy Space Center in Florida.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched NASA and Kennedy visitor information for exact IMAP launch attendance; no reliable count was found.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.nasa.gov/news-release/nasa-noaa-launch-three-spacecraft-to-map-suns-influence-across-space/
```

**New quote**

```text
Wednesday, Sept. 24, 2025.
```

**New wrong_detail**

```text

```

**New note**

```text
NASA confirms the launch date and location but gives no exact visitor count. No opened source establishes or contradicts 6,324 spectators.
```

Owner decision:


## u-08

**Claim**

```text
On February 7, 2026, the Milan Olympic Village in Italy served exactly 10,000 eggs.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched the IOC Games statistics and day-specific catering reports; the IOC gives a daily service figure but no exact February 7 tally.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.olympics.com/ioc/news/milano-cortina-2026-in-numbers-record-engagement-efficient-delivery-world-class-performance
```

**New quote**

```text
10,000 eggs
```

**New wrong_detail**

```text

```

**New note**

```text
The IOC reports this under daily servings across six Olympic Villages. It provides no count specifically for Milan on February 7, and does not establish an exact day-specific total. That scope mismatch does not disprove the claim.
```

Owner decision:


## u-10

**Claim**

```text
The Apple Store in Palo Alto, California, sold exactly 2,416 iPhone 17 units on September 19, 2025.
```

**Review reason:** new verdict is cannot_settle.

**Old label:** cannot_settle

**Original expected_verdict:** (empty)

**Original expected_outcome:** unable_to_decide

**Old source_url_1**

```text

```

**Old source_shows_1**

```text
Searched Apple’s launch account and SEC filing plus store-level launch-day sales queries; no reliable store count was found.
```

**New verdict:** cannot_settle

**New source_url**

```text
https://www.apple.com/newsroom/2025/09/the-latest-iphone-apple-watch-and-airpods-arrive-in-apple-store-locations/
```

**New quote**

```text
PHOTOS September 19, 2025
```

**New wrong_detail**

```text

```

**New note**

```text
Apple's launch-day report confirms the worldwide launch but gives no store-level unit sales. No opened source confirms or contradicts 2,416 iPhone 17 units at the Palo Alto store that day.
```

Owner decision:
