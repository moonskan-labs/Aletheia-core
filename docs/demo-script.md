# Demo video script

A 2–3 minute video for the ODSC × Nebius submission. There is no live demo day: judges
score this video and the repository. Target length: **2:30**.

Judging weights, and where the video covers each:

| Criterion | Weight | Shown in |
| --- | ---: | --- |
| Sourced and verifiable answers | 30% | Scenes 3, 4 and 5: quotations open on the source page; cannot settle instead of a guess |
| Works end to end | 25% | Scenes 2–6: real live runs through the web client and API |
| Usefulness | 20% | Scenes 1 and 4: a named user with a real claim to check |
| Agent design | 15% | Scene 3: plan, search, read, judge, check, follow up; Python in control |
| Use of Token Factory and Tavily | 10% | Scene 3: the research log names every call |

## Before recording

- **Branch:** record from `main` after #32, #36, #37 and #38 merge. Before that, the client
  has no passage links or real recordings.
- **Settings:** `.env` from `.env.example` (DeepSeek V4 Pro, simple loop, 120 s timeout).
  Never show `.env` or a terminal that prints it.
- **Start fresh:** delete `data/aletheia.sqlite3` (or point `ALETHEIA_DATABASE_PATH` at a
  new file) so the first submissions are real runs, not saved results.
- **Rehearse the three claims live the same day.** Answers vary between runs: on the 77
  trusted claims, two DeepSeek runs differed on 13. These three were right in both runs.
  If one comes back differently on the day, use it as it is, or swap in another from the
  list at the end. Never edit a result.
- **Waiting time:** runs take 15–50 s. Cut or speed up the waiting, and say so on screen
  ("sped up 4×"). Don't cut the progress log entirely: it shows that the run is real.
- **Browser:** the client at 1440 px wide, zoomed to 125%, so the quotations are readable.

## Script

`[00:00–00:20]` **1. The problem**

> Screen: the entry page, claim field empty.

<!-- TODO: the demo's named user. The wording below assumes a health reporter. -->

"This is Aletheia. Say you're a health reporter, and a draft says 610,000 people died of
malaria in 2024. Before that goes out, you need to know whether it's right, and you need
to be able to show where the answer came from. Aletheia checks a claim against the live
web and answers true, false or cannot settle. Every true or false verdict includes a
quotation you can check."

`[00:20–01:00]` **2–3. A live check, and how it works**

> Type: `An estimated 610,000 people died of malaria worldwide in 2024, according to WHO.`
> Submit. Show the progress log as it runs.

"It's running live now. One model call on Nebius Token Factory plans up to three
searches. Tavily runs them at the same time and reads the best pages. Then one more
model call reads those pages and gives a verdict, with quotations copied word for word."

> Point at the research log lines that name Token Factory and Tavily calls, and the
> counts line.

"Python stays in control throughout. The model only writes queries and a verdict. The
code runs every search, enforces the limits, and checks every quotation against the
saved page. A quotation that isn't on the page is thrown out, and a verdict with no
valid quotation becomes cannot settle."

`[01:00–01:30]` **4. The answer, and its evidence**

> The result: **True**. Click the first quotation in the report.

"True. Here's the quotation it relied on." *(The source page opens at the highlighted
passage.)* "That's the source page, at the exact sentence. You don't have to trust the
verdict: you can check it in one click."

> Say the source's name as it appears on the day, for example "the WHO's World Malaria
> Report".

> Show the evidence pane: the pages read, and any passage checked but not admitted.

"It also lists every page it read, and any passage it checked but didn't accept."

`[01:30–01:55]` **5. A wrong figure**

> Type: `The WHO African Region accounted for 75% of global malaria cases in 2024.`
> Submit; speed up the wait.

"Now a figure that's close, but wrong."

> The result: **False**. Click the quotation.

"False. The quotation shows the share the source actually gives."

`[01:55–02:15]` **6. When it can't tell**

> Type: `Exactly 87 hikers reached Mount Whitney's California summit on July 1, 2001.`
> Submit; speed up the wait.

"And when the web doesn't have the answer?"

> The result: **Cannot settle**, with its limitation.

"Cannot settle. The pages Aletheia found do not establish how many hikers reached the
summit that day, so it leaves the claim unresolved."

`[02:15–02:30]` **7. Saved and measured**

> Resubmit the first claim: the saved result appears at once. Then switch to the README's
> accuracy table.

"Every run is saved. Ask again, and you get the same result instantly, with no new
calls. We measured it with live search on 77 claims whose labels we checked: 66
right, in two separate runs. When it answers true or false, it's right about nine
times in ten. Aletheia: evidence first."

## Spare claims

Also right in both DeepSeek runs on the 77, each under 45 s:

| Expected | Claim |
| --- | --- |
| True | IMAP launched for NASA from Kennedy Space Center in Florida on September 24, 2025. |
| True | The Milano Cortina 2026 Winter Olympics in Italy included 116 medal events. |
| False | A New Glenn rocket carried NASA's IMAP from Florida on September 24, 2025. |
| False | WHO placed the worldwide number of new malaria cases in 2015 at 273 million. |
| Cannot settle | Exactly 6,324 visitors watched the September 24, 2025, IMAP launch from Kennedy Space Center in Florida. (45–51 s) |

## After recording

- Add the video link to the top of the README and to the submission form.
- Check the length (under 3:00) and that every result on screen is a real, unedited run.
