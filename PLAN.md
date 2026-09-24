# Plan — Demo 4: PSA Global Terminal Map (a showcase for the `web-stack-advisor` skill)

Status: **implemented**, at [`demos/psa-terminal-map/`](demos/psa-terminal-map/README.md) — see that folder's `README.md` for what was actually built (27 real, sourced PSA terminals rather than the ~30-45 estimated below) and `PROMPT.md` for the condensed build prompt. This file is kept as the original planning brief.

## Context

`demos/` currently holds three demos, and all three exist to back *blog claims* (Django vs FastAPI+React for a labeling tool; long-running jobs on Windows). Nothing in the repo showcases the `web-stack-advisor` skill itself — the skill is ~530 lines of Markdown tables that a reader has to take on faith.

This demo makes the skill visible and checkable. It is a static, no-backend interactive web app showing PSA International's container terminals worldwide, and it is built at **rung 1 of the skill's own ladder** because that is exactly what the skill recommends for this use case. The app then shows its own working: a build-trail panel replaying the 12-functionality verdict for itself, and a live advisor where the visitor picks a use case and sees the skill's recommendation derived in front of them.

The point it proves: *the skill's advice is a function you can run, not an opinion.* The advisor logic is a pure JS module with unit tests asserting that all eight documented use cases produce the documented stacks — so the demo verifies the skill rather than just displaying it.

Decisions already taken:

- Subject: PSA International's own ports, not global container ports generally.
- Data: real researched figures with sources, not synthetic.
- Skill showcase: build-trail panel **and** live advisor (both, not either).

## Where it goes

New folder `demos/psa-terminal-map/`, following the existing demo conventions exactly (`README.md` + `PROMPT.md` + code; H1 is `# Demo 4 — PSA global terminal map`).

It deliberately does **not** use `demos/sample-data/` — that fixture is the shared ticket-triage scenario for demos 1 and 2. This demo has its own domain data. The README should say so, so the shared-data exception stays scoped to where it was justified.

## Stack (and why it is the stack)

Per `.claude/skills/web-stack-advisor/references/use-cases.md`, "share a chart / pipeline that ends in a page" needs functionalities 1, 2, 3 → **rung 1: static HTML + D3 + Tailwind**. No server, no persistence, no auth. The app eating its own dog food is the argument.

- **D3 v7** via ESM CDN import, per [docs/javascript.md](docs/javascript.md) (`https://cdn.jsdelivr.net/npm/d3@7/+esm`), matching [dataviz-python-js/d3-interactive-web/](dataviz-python-js/d3-interactive-web/README.md).
- **Tailwind + daisyUI** via CDN browser build (`@tailwindcss/browser@4` + daisyUI's CDN stylesheet), the exact Node-free route already documented in the skill's `references/tools/tailwind.md` and used by [demos/labeling-django/](demos/labeling-django/README.md). This is also what `references/use-cases.md` prescribes for "business users, read-only": static D3 polished with a Tailwind kit.
- **A small `css/style.css`** alongside Tailwind, holding only the viz palette as CSS custom properties with a `prefers-color-scheme: dark` override — same pattern as `d3-interactive-web/css/style.css`, because chart code must resolve to `var(--series-N)` rather than raw hex.
- **No build step, no bundler, zero npm dependencies.** `package.json` exists only for `"type": "module"` and the test script.
- Served with the existing root tooling: `npm run serve -- demos/psa-terminal-map`.

Before writing any chart code, load the `dataviz` skill for palette/mark/legend conventions.

## The page: three acts on one scrolling page, sticky nav

### Act 1 — the map (the product)

- World map, `d3.geoNaturalEarth1`, land drawn from a **vendored** `data/world-110m.json` (world-atlas 110m TopoJSON, Natural Earth derived, public domain — attributed in the README). Vendored rather than CDN-fetched so the demo works offline and is reproducible; `topojson-client` imported from the CDN for the mesh/feature conversion.
- PSA terminals as proportional circles: `d3.scaleSqrt` on designed capacity, coloured by PSA's five regions (Southeast Asia; Northeast Asia; Middle East, South Asia, Africa, Türkiye; Europe; Americas).
- `d3.zoom` pan/zoom, hover tooltip, click → detail card (berths, quay length, depth, terminal area, quay cranes, designed capacity, source link).
- Two companion charts, **cross-filtered with the map**: capacity by region, and a top-15 terminal ranking. Clicking a region chip or a bar filters the map and the other chart. Cross-filtering is what justifies D3 over a static image, and it reuses the state pattern from `d3-interactive-web` (`app.js` is the only state holder; every other module renders what it is handed).
- A sourced KPI row (countries, terminals, group TEU handled).

### Act 2 — "Why this stack" build trail

Rendered from `data/advisor-model.json` + `data/this-app-verdict.json`, never hardcoded in HTML, so it is visibly data-driven:

- The 12-functionality table for *this* app: functionality, needed (tick/cross), tool chosen, one-line why.
- The five-rung ladder as a visual, rung 1 lit, with the escalation triggers from `references/use-cases.md` shown as "what would push this app up a rung" (e.g. reviewers needing accounts → rung 4, Django).
- Each higher rung links to the demo in this repo that already occupies it — demos 1/2/3 become the proof for rungs 4, 5 and functionality 12. This ties the four demos into one story.

### Act 3 — the live advisor

- Input: the skill's five intake questions from `SKILL.md`'s `## Procedure` (audience; one user or many; saves anything; anything slower than a few seconds; does another system call it), plus a shortcut row of the eight documented use cases.
- Output: the derived functionality set (the 12 light up), the recommended rung and stack, the "why", the audience modifier applied, and flagged gaps — server-side authz, the Windows job-queue traps from `references/background-jobs.md`, and which tool notes are documentation-only rather than run in this repo.

## Files

```
demos/psa-terminal-map/
  README.md                  # per repo convention, ends with Run it / Manual checks / Reproducing
  PROMPT.md                  # saved build prompt, same 3-part shape as the other demos
  package.json               # private, "type": "module", test script, zero deps
  index.html                 # single page, one <script type="module" src="js/app.js">
  css/style.css              # viz palette custom properties + dark-mode override only
  js/app.js                  # state + orchestration (the only state holder)
  js/data.js                 # loads JSON, derives region/ranking aggregates
  js/map.js                  # projection, land, terminal circles, zoom
  js/charts.js               # region bar + top-15 ranking bar
  js/detail.js               # terminal detail card
  js/filters.js              # region chips, search box
  js/tooltip.js              # shared singleton tooltip (mirrors d3-interactive-web/js/charts.js)
  js/advisor.js              # PURE recommendation logic — the tested core
  js/advisorUi.js            # Act 3 rendering
  js/buildTrail.js           # Act 2 rendering
  data/terminals.json        # researched PSA terminals, each with sources[]
  data/world-110m.json       # vendored land topology (public domain, attributed)
  data/advisor-model.json    # the 12, the ladder, 8 use cases, audiences, escalations, cautions
  data/this-app-verdict.json # this app's own 12-row verdict
  tests/advisor.test.js
  tests/dataShape.test.js
```

`js/advisor.js` encodes the skill's rules as data-driven logic, not `if` soup:

- **Rule C scoring** (`references/functionalities.md`, "How to use the table"): `{3,6}` → rung 2; each tick from 7 onward pushes toward rung 4; ticks at **both** 4 and 5 → rung 5 / two projects, gated on the app-like-UI or external-consumer test.
- **Rule D escalations** (`use-cases.md`, "When to escalate a rung") and the **audience modifier** applied after the functionality pick.

## Data research (the slowest step — do it first)

PSA publishes per-terminal fact sheet PDFs under `globalpsa.com/wp-content/uploads/` (e.g. `PSA-ANTWERP.pdf`, `BUSAN-TERMINALS.pdf`, revision-dated 2026.04) carrying berths, quay length, depth, area, designed capacity and quay cranes — a consistent schema across terminals. `globalpsa.com/global-network/` and the Wikipedia PSA International article give the network list.

Rules for this step, stated in the README:

- **Scope: deepsea container terminals only** (~30-45 entries). PSA's full footprint is 70+ deepsea/rail/inland terminals across 180+ locations in 45 countries; inland and rail terminals are explicitly out of scope and the README says so rather than implying full coverage.
- Every record carries `sources: [url]` and the retrieval date. The README gets a **Data provenance** section: figures are as-published by PSA and may be stale; this is a demo dataset, not an authoritative one.
- **Fields PSA does not publish are `null`, never invented.** The UI renders "not published" for nulls. Coordinates come from the port's public location, rounded, and are flagged approximate — they position a dot, they are not survey data.
- If research turns up materially less than expected for some regions, ship what is sourced and say which terminals were left out and why, rather than padding.

## Tests

`node --test` (Node v20.18.1 verified on this machine, so the stable built-in runner is available — `d3-interactive-web` hand-rolled a runner only because its Node predated it; the README should note this). Zero dependencies, per `docs/javascript.md`.

- `tests/advisor.test.js` — **the load-bearing test**: every one of the eight use cases in `references/use-cases.md` must produce the stack that file documents; the 4+5 two-projects rule; the three escalation transitions; the audience modifier changing the pick without changing the functionality set. This is what turns "the skill is useful" into a claim the repo checks.
- `tests/dataShape.test.js` — every terminal has the required fields, a non-empty `sources[]`, coordinates in range, and capacity either a positive number or explicitly `null`.

D3 rendering is checked by eye, per the existing convention.

## Docs to update in the same change

Required by `CLAUDE.md`'s "Keeping docs in sync":

- `demos/README.md` — "three demos" → four, a new row in the `| Demo | Backs | Proves |` table, and a line in "Shared scenario" noting this demo intentionally sits outside the ticket-triage scenario.
- `README.md` (root) — the `demos/` bullet in "Structure" (currently "three runnable demos"), and the "Tooling scope" paragraph naming which tools `demos/` exercises (now also D3 + Tailwind-with-daisyUI at rung 1).
- `CLAUDE.md` — the `demos/` bullet, the "Explored in this repo" list, and the paragraph tying the skill to `demos/`.
- `docs/javascript.md` — two short additions: vendoring a third-party data file into a stage's `data/` (when and how to attribute), and `node --test` as the runner for zero-dependency stages on Node 18+.
- `blog/README.md` — the demos line ("three runnable demos") and what this one backs. The blog **post** is not touched: `docs/blog-style.md` forbids referencing this repo from a post.
- `.gitignore` — a commented note that this demo generates nothing, so it needs no entry (the file's convention is to explain, including when no entry is needed).
- The skill, to keep it consistent with `CLAUDE.md`'s instruction: mark `references/use-cases.md`'s "share a chart" row and `references/ui-kits.md` / `references/tools/tailwind.md` as now backed by a runnable demo. **Stale line already fixed (2026-09-24):** `SKILL.md`'s Cautions now states per-tool status (FastAPI and Tailwind run in the repo; Streamlit and Dash documentation-only) instead of a blanket "have not been run" claim.

## Verification

1. `npm install` at the repo root if `node_modules` is absent, then `npm run serve -- demos/psa-terminal-map`, open `http://localhost:8080`.
2. Manual checks, written into the README as a numbered list: map renders with all terminals; hovering shows a tooltip; clicking a terminal opens the detail card with a working source link; clicking a region chip filters map + both charts together; clearing the filter restores everything; zoom/pan works; the page is legible at phone width and in dark mode.
3. `cd demos/psa-terminal-map && npm test` — both test files pass.
4. Cross-check three terminal records at random against the cited source URL, and record in the README that this check was done (the repo's "verified, not just asserted" convention).
5. No `git commit` — per `CLAUDE.md`, the user commits. Provide a suggested commit message instead.

## Out of scope

Deployment (the repo's `deploy/` material is unrelated and this demo is local-only), live PSA data feeds, inland/rail terminals, and any backend. If the map later wants live throughput, that is the skill's own escalation story — rung 3, a small API — and the README should say so rather than building it.
