# The simple search-and-verdict loop

An alternative to the staged pipeline for one claim. It is off by default. Turn it on
with `ALETHEIA_PIPELINE=simple` alongside `ALETHEIA_RESEARCH_ENABLED=true`:

```sh
ALETHEIA_RESEARCH_ENABLED=true ALETHEIA_PIPELINE=simple uv run --locked aletheia
```

The API, the saved records and the event types are unchanged, so existing clients
keep working.

## What it does

1. **Plan.** One model call writes up to three search queries from the claim. If that
   call fails, the claim text itself is the query.
2. **Search and read.** Each query runs through Tavily search. Results are taken in
   turn across queries (every query's best hit before any query's second). Social and
   video sites are not read, and government, academic and international-body sites
   are read first. Duplicates are dropped by URL and by page content, and up to six
   pages are extracted and saved.
3. **Judge.** One model call (`aletheia.one_call`, the call the trusted evaluation
   measures) sees the claim and the most relevant passages of up to six pages. It
   returns `true`, `false` or `cannot_settle`, up to four quotations and a reason.
4. **Check the quotations.** A quotation counts only if it is found word for word in
   the saved page. A `true` or `false` answer with no such quotation is not published.
5. **Check the verdict against its quotations.** A second, small model call sees only
   the claim and the accepted quotations and says which way they point. If they point
   the opposite way to the verdict, the verdict is withdrawn and treated as
   `cannot_settle`. An unclear reading leaves the verdict standing.
6. **Follow up once.** If the answer is `cannot_settle`, one more plan call gets the
   model's reason as "what is missing", up to three new pages are read, and the judge
   call runs once more over all pages. Then the loop stops.

Page text reaches the model only as data in the user message. The instructions are
fixed and tell the model not to follow instructions found inside pages.

## When it stops, and what it reports

| Situation | Status | Stop reason | Verdict |
| --- | --- | --- | --- |
| True or false with a located quotation | completed | `evidence_sufficient` | true / false |
| Not settled after the follow-up | completed | `budget_exhausted` | none |
| Search found nothing, or no page could be read | completed | `no_useful_query` | none |
| The model's answer could not be used | partial | `invalid_task_output` | none |
| Search or retrieval failed part-way | partial | `provider_failure` | none |
| Time or call limit reached | partial | the limit's name | none |
| Credentials rejected or quota exhausted | failed | `provider_failure` | no result |

Without a verdict the result is `unable_to_decide` with `insufficient_evidence`, and
the model's reason is listed under limitations.

## Limits per claim

At most 6 model calls, 6 searches and 10 page extractions, within 150 seconds.

## What it does not do

It does not produce the "almost" verdict, qualification flags, component findings or
source provenance fields. Those belong to the staged pipeline.

## Measuring it

`scripts/evaluate_research.py --pipeline simple` runs the loop through the same
runner as the staged pipeline, including `--replay-evidence` on saved pages.
