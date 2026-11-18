# Aletheia web client

Companion demo client for the backend described in the [design document](../docs/design.md), sections 9 and 11. It is a static React + TypeScript app built with Vite. It never hosts or exposes the backend.

## Modes

| Mode | How to run | What it does |
| --- | --- | --- |
| Replay (default) | `npm run dev` | Plays bundled recordings from `src/fixtures/`. No backend calls; every view is labeled **Recorded investigation**. This is the only mode allowed on a hosted deploy. |
| Live | `VITE_DATA_SOURCE=live npm run dev` | Talks to the local backend through the dev-server proxy at `/api`. Set `ALETHEIA_API_URL` if the backend is not on `http://127.0.0.1:8000`. Localhost only. This command starts only the client; run the backend separately ([README](../README.md#quickstart)). On load the client calls `GET /health`, and the claim field is enabled only when the backend answers **and** reports `research_enabled: true`. Otherwise it explains why (unreachable, or research not enabled yet). |

## Commands

```sh
npm install
npm run dev      # http://127.0.0.1:5173
npm run build    # type-check and build to dist/
npm run lint
npm test         # hook and form behavior (Vitest + jsdom)
```

## Screens

- **Entry:** the claim field is always the first thing on the page. In live mode it submits; while a submission is pending the button reads "Starting investigation…" and further clicks are ignored. In replay mode the field is disabled, with a note that live investigation needs the backend, which is still being built. Below it, in live mode, **Recent investigations** lists the 10 newest saved runs (`GET /investigations?limit=10`) with their result or status and time; choosing one opens its saved report without a new run. The list loads whenever the home page shows and whenever the backend becomes reachable (so "Retry connection" brings it in), and is left out when the backend can't answer. Sample investigations are listed below that.
- **Researching:** the claim headline, the latest step, and the live progress log.
- **Report** (saved samples open straight to it; "Replay research steps" plays the recorded progress), in visual direction B ([`design/visual-direction.md`](../design/visual-direction.md)): the claim, the result label just below it in its label colour (smaller than the claim), and one mono line of run facts. Below, the report on the left (the evidence-linked conclusion, any correction or caveat, what was checked, limitations, and the collapsed research log) and the evidence pane on the right.
- **Results that fail to load:** if research ends but fetching the report fails, the page says so and offers "Retry loading results", which never starts a new investigation.
- **Evidence pane:** shows one piece of evidence at a time, numbered as cited: relation, source, the exact excerpt, why it counts, and a link to the original. Where the excerpt is plain prose, the link opens the source at that passage (a URL text fragment; browsers without support open the page as usual). A collapsed list names every page the run read, quoted or not. Choosing a citation in the report, or a numbered tab in the pane, selects it (`aria-pressed`). Passages checked but not admitted are collapsed at the bottom of the pane. Below 900px the pane stacks under the report, and choosing a citation scrolls to it.

## Status and caveats

- `src/api/types.ts` is **reconciled** with `src/aletheia/contracts.py` and the backend's `/openapi.json` for investigations, context, links, errors and `/health`. Results and evidence are exercised with captured backend responses; event names are checked against the backend contract, and payload fields are read defensively.
- If the progress stream closes before research finishes (for example, `/events` returns 404 on a backend without the research pipeline), the page says live progress isn't available instead of staying on "Researching".
- Two recordings in `src/fixtures/live/` are real, unedited runs of the search-and-verdict loop against Token Factory and Tavily (2026-11-16): one true, one false. They were checked for secrets before being added. The third recording is invented sample data (`sample: true`), and the page says so.
- The research log names each provider call (Token Factory model call, Tavily search, Tavily page read) and its summary line counts searches, pages read and model calls. Two step types that only announce the next line are left out of the finished log.
- Clarification, failed and partial results render in the shared layout, but their full designs and sample recordings come in a follow-up.
- The refresh and comparison screens are not built yet.

### Phase 1 backend integration

The client subscribes to all 39 backend event names and describes the Phase 1 stop
reasons. Unsupported-method responses show the saved explanation even though no
truth verdict exists. A partial result stopped by `semantic_rejection` or
`invalid_task_output` shows “No confirmed decision” with the collected evidence,
without presenting an insufficient-evidence verdict or qualification caveat.

The Phase 1 regression recordings come from the API, worker and SQLite with
synthetic providers. Regenerate only these recordings from the repository root:

```sh
uv run --locked python web/scripts/capture_backend_fixtures.py . web/src/fixtures/backend unsupported-method unconfirmed-decision quoted-explanation deadline-before-confirmation
```

Earlier recordings remain historical compatibility cases, including Almost and the
older partial-result behavior. New Phase 1 runs do not publish Almost, and a deadline
before a pending verdict is confirmed fails with no result.
