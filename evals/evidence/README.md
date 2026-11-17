# Saved evidence pages

Page text fetched during evaluation runs, kept so a changed pipeline step can be replayed
on the same pages without new searches.

- `index.csv`: one row per page: claim, URL, retrieval time, SHA-256 of the text, length,
  and which run fetched it.
- `pages/<claim id>.json.gz`: the pages for that claim, with the full text as fetched.
  A page fetched by both runs with identical text is stored once.

Current contents: 503 pages for the 80 tuning claims, from the two Nov 16 runs
(`20261116-tuning-decision-gate`, `20261116-tuning-qwen235`). Pages from the Nov 15 runs
were not kept and are not here. These pages are what those two pipelines chose to fetch;
they are not a guarantee that the answer to each claim is among them.
