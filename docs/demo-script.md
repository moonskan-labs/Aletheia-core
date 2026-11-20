# Demo video script

A 2–3 minute video for the ODSC × Nebius submission. There is no live demo day: judges
score this video and the repository. Target length: **2:30**.

Judging weights, and where the video covers each:

| Criterion | Weight | Shown in |
| --- | ---: | --- |
| Sourced and verifiable answers | 30% | Scenes 4 and 5: each quotation highlighted and opened on its source page; Scene 6: no guess when the pages don't say |
| Works end to end | 25% | Scenes 2–6: real live runs through the web client and API |
| Usefulness | 20% | Scenes 1 and 4: a health reporter checking a figure before it is published |
| Agent design | 15% | Scene 3: plan, search, read, judge, check quotations; Python in control |
| Use of Token Factory and Tavily | 10% | Scene 3: the research log names every call |

## Before recording

- **Branch:** record after #43, #44 and #47 merge into `main`; they hold the current web
  client (centred search, one-column report, highlighted quotations). If they haven't
  merged by recording time, record from the `ui/merge-layout-c` branch.
- **Settings:** `.env` from `.env.example` (DeepSeek V4 Pro, simple loop, 120 s timeout).
  Never show `.env` or a terminal that prints it.
- **Start fresh:** point `ALETHEIA_DATABASE_PATH` at a new file, for example
  `data/demo.sqlite3`, so the first submissions are real runs, not saved results, and
  Recent investigations holds only the demo claims. Your existing history stays in
  `data/aletheia.sqlite3`.
- **Rehearse the three claims live the same day.** Answers vary between runs: on the 77
  trusted claims, two DeepSeek runs differed on 13. These three were right in both runs.
  If one comes back differently on the day, use it as it is, or swap in another from the
  list at the end. Never edit a result.
- **Waiting time:** runs take 15–50 s. Cut or speed up the waiting, and say so on screen
  ("sped up 4×"). Don't cut the progress log entirely: it shows that the run is real.
- **Browser:** the client at 1440 px wide, zoomed to 125%, so the quotations are readable.
  Use dark mode: the palette was designed for it.

## Script

`[00:00–00:20]` **1. The problem**

> Screen: the home page, search box empty.

"This is Aletheia. Say you're a health reporter, and a draft says 610,000 people died of
malaria in 2024. Before that goes out, you need to know whether it's right, and you need
to be able to show where the answer came from. Aletheia checks a claim against the live
web and says whether it's true, false, or can't be settled from what it found. Every
true or false verdict includes a quotation you can check."

`[00:20–01:00]` **2–3. A live check, and how it works**

> Type: `An estimated 610,000 people died of malaria worldwide in 2024, according to WHO.`
> Click **Verify**. Show the progress log as it runs.

"It's running live now. One model call on Nebius Token Factory plans up to three
searches. Tavily runs them at the same time and reads the best pages. Then one more
model call reads those pages and gives a verdict, with quotations copied word for word."

> While it runs, point at the log lines that name Token Factory and Tavily calls. (Once
> the run finishes, the log folds into one line under **What we checked**: click
> **Research log** to open it again.)

"Python stays in control throughout. The model only writes queries and a verdict. The
code runs every search, enforces the limits, and checks every quotation against the
saved page. A quotation that isn't on the page is thrown out, and a verdict with no
valid quotation becomes 'can't settle'."

`[01:00–01:30]` **4. The answer, and its evidence**

> The result: **True**. Click citation **[1]** in the summary: the **Evidence** box
> below shows that quotation, highlighted.

"True. Here's the quotation it relied on, word for word from the page."

> Click **Open the original at this passage**: the source page opens with the sentence
> highlighted. Say the source's name as it appears on the day, for example "the WHO's
> World Malaria Report".

"That's the source page, at the exact sentence. You don't have to trust the verdict:
you can check it in one click."

> Back in the report, open **N pages read** at the bottom of the Evidence box.

"It also lists every page it read, not just the ones it quoted."

`[01:30–01:55]` **5. A wrong figure**

> Type: `The WHO African Region accounted for 75% of global malaria cases in 2024.`
> Click **Verify**; speed up the wait.

"Now a figure that's close, but wrong."

> The result: **False**. Click the citation that follows the real share (if the summary
> has one sentence, the citations all follow it).

"False. Each number sits after the sentence it supports, and this quotation shows the
share the source actually gives."

`[01:55–02:15]` **6. When it can't tell**

> Type: `Exactly 87 hikers reached Mount Whitney's California summit on July 1, 2001.`
> Click **Verify**; speed up the wait.

"And when the web doesn't have the answer?"

> The result: **Insufficient evidence**, with its limitation.

"Insufficient evidence. The pages it found don't give a summit count for that day, so
it doesn't guess."

`[02:15–02:30]` **7. Saved and measured**

> Go back to the home page: the three claims are under **Recent investigations**. Click
> the first one: its saved report opens at once. Then switch to the README's accuracy table.

"Every run is saved. Your past checks are right here, and opening one shows the same
result instantly, with no new calls. We measured it with live search on 77 claims whose
labels we checked: 66 right, in two separate runs. When it answers true or false, it's
right about nine times in ten. Aletheia: evidence first."

## Spare claims

Also right in both DeepSeek runs on the 77, each under 45 s:

| Expected | Claim |
| --- | --- |
| True | IMAP launched for NASA from Kennedy Space Center in Florida on September 24, 2025. |
| True | The Milano Cortina 2026 Winter Olympics in Italy included 116 medal events. |
| False | A New Glenn rocket carried NASA's IMAP from Florida on September 24, 2025. |
| False | WHO placed the worldwide number of new malaria cases in 2015 at 273 million. |
| Insufficient evidence | Exactly 6,324 visitors watched the September 24, 2025, IMAP launch from Kennedy Space Center in Florida. (45–51 s) |

## After recording

- Add the video link to the top of the README and to the submission form.
- Check the length (under 3:00) and that every result on screen is a real, unedited run.
