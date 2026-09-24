# Build prompt: Demo 4 — PSA global terminal map

Saved for future reference — hand this to a fresh Claude Code session to rebuild this demo from
scratch (e.g. in another repo with the same conventions). See [`README.md`](README.md) for what
was actually built and how to run it. This demo's own planning brief, `PLAN.md`, was written and
committed before implementation and is the fuller version of this prompt.

---

Build a static, no-backend demo at `demos/psa-terminal-map/` inside this repo, following its
existing conventions (`CLAUDE.md`, `docs/javascript.md`, the other `demos/` folders). Its purpose
is different from the other three demos: instead of backing one blog claim, it showcases the
`web-stack-advisor` skill itself — a working app built at the rung the skill recommends, plus a
build-trail panel and a live advisor rendering the skill's own rules as data and running its
actual scoring logic.

**Stack (rung 1 per `references/use-cases.md`'s "share a chart" row, functions 1/2/3 only):** D3
v7 via ESM CDN import, Tailwind 4 + daisyUI 5 as CDN browser builds (no Node, no build step, same
route `demos/labeling-django/` verified), a small `css/style.css` holding only the dataviz skill's
validated palette as CSS custom properties (reuse `dataviz-python-js/d3-interactive-web/css/style.css`'s
exact palette values, light and dark, so this app and that stage read as one system — re-run
`scripts/validate_palette.js` from the `dataviz` skill to confirm rather than assuming). Zero npm
dependencies; `package.json` exists only for `"type": "module"` and `node --test` as the test
script. Serve with `npm run serve -- demos/psa-terminal-map` (the repo-root `http-server`).

**Data research first, before any code** — the slowest step. Research PSA International's real
deepsea container terminals (berths, quay length, depth, terminal area, quay cranes, designed
capacity TEU/yr) from PSA's own site, per-terminal PDFs, and terminal/port-authority sites.
Deepsea only, no inland/rail — expect roughly 30-45 terminals across five PSA regions (Southeast
Asia; Northeast Asia; Middle East, South Asia, Africa, Türkiye; Europe; Americas). Every record
carries `sources: [url]` and a retrieval date; every field PSA doesn't publish is `null`, never
invented; coordinates are the port's approximate public location (`coordinatesApproximate: true`),
not survey data. Ship what's genuinely sourced — say in the README which regions came up short
rather than padding. Separately source one real, company-wide "group TEU handled" statistic
(a distinct figure from any per-terminal capacity) for the KPI row.

Also vendor `data/world-110m.json` — world-atlas's 110m land TopoJSON (public domain, Natural
Earth-derived) — rather than fetching it from a CDN at runtime, so the page works offline. Attribute
it in the README per `docs/javascript.md`'s vendoring convention.

**The page, three acts on one scrolling page with sticky nav:**

1. **The map** — `d3.geoNaturalEarth1` projection, land from the vendored topology via
   `topojson-client`, terminals as `d3.scaleSqrt`-sized circles colored by region (fixed
   categorical order, never cycled), `d3.zoom` pan/zoom, hover tooltip, click → detail card. Two
   companion charts cross-filtered with the map: capacity by region, and a top-15 ranking —
   clicking a region chip or a region bar sets a shared filter; the region chart itself always
   shows all five regions so there's always something to click back to. A sourced KPI row
   (countries, terminals, group TEU handled).
2. **Why this stack** — rendered from `data/advisor-model.json` (the skill's 12 functionalities,
   five-rung ladder, eight use cases, audience table, three escalation rules — encoded as data,
   not hardcoded HTML) and `data/this-app-verdict.json` (this app's own 12-row verdict, written by
   hand so each row argues in this app's own words). The ladder highlights rung 1 and links each
   higher rung to whichever other demo in this repo already occupies it.
3. **Try the advisor** — a shortcut row of the skill's eight documented use cases, plus a form for
   the skill's five intake questions (audience; one user or many; saves anything; slower than a
   few seconds; does another system call it). Both paths run through the same pure `js/advisor.js`
   functions and light up the 12 functionalities, show the recommended rung/stack, the reason
   (base pick, an escalation, or the audience modifier), and flagged gaps (background-jobs Windows
   traps, doc-only-vs-run tool status).

**`js/advisor.js` is the tested core** — pure functions, no DOM:
- `recommendStack(needsSet, options)`: Rule C base pick from ticks (7-11 → Django; 4 alone →
  FastAPI; 3+6 → Streamlit, or Dash if `layoutControl`; else static D3), then three named Rule D
  escalations (Streamlit/Dash→Django on `needsAccountsWithDifferentVisibility`; FastAPI→Django on
  `reimplementingAuthOrmAdmin`; Django→React+API on `appLikeUi`/`externalConsumer`/
  `frontendEngineerOwnsUi`, also the 4+5-ticked-together two-projects gate), then the audience
  modifier applied last (business-interactive escalates to Django; business-readonly moves
  Streamlit to Dash) — never mutating the input Set.
- `recommendForUseCase(useCase)`: looks up a documented use case's needs/flags and runs them
  through `recommendStack`.
- `deriveNeedsFromIntake(answers)`: a judgment-call mapping from the five intake questions to a
  tick set, for the free-form advisor path.
- `buildGaps(needsSet)`: cross-cutting cautions (functionality 12 doesn't drive the rung by
  itself; authorization must be server-side).

**Tests (`node --test`, zero dependencies):**
- `tests/advisor.test.js` — the load-bearing one: every documented use case (the multi-user
  prototype case is split into two rows, default-UI and app-like-UI, since it has one
  functionality set and two documented outcomes) produces its documented stack; the 4+5
  two-projects rule; all three escalation transitions; the audience modifier changing the pick
  without changing the functionality Set object passed in.
- `tests/dataShape.test.js` — every terminal has every required field, a non-empty sourced array
  of real URLs, in-range `[lon, lat]` coordinates, and every numeric field is a positive number or
  explicitly `null`, never a placeholder.

D3 rendering itself is checked by eye, per this repo's convention — open the page, check every
manual item in the README (filters, tooltip, detail card + source link, cross-filtering, zoom/pan,
phone width, dark mode).

**Docs to update in the same change** (`CLAUDE.md`'s "Keeping docs in sync" rule): `demos/README.md`
(four demos, new table row, shared-scenario note), root `README.md` (demos bullet, tooling scope),
`CLAUDE.md` (demos bullet, "Explored in this repo", the skill/demos paragraph), `docs/javascript.md`
(vendoring convention, `node --test` on Node 18+ superseding d3-interactive-web's old hand-rolled
runner), `blog/README.md`, `.gitignore` (a comment explaining no entry is needed), and the skill
itself (mark the "share a chart" use-case row, `ui-kits.md`'s daisyUI row, and `tools/tailwind.md`'s
status line as now also backed by this demo).

Verify by actually running: install root `node_modules` if absent, serve the page, click through
every manual check, run both test files, and spot-check three terminal records at random against
their cited source URLs — record in the README that this was done. No `git commit` — the user
commits; provide a suggested message instead.
