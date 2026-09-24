# Demo 4 — PSA global terminal map

A showcase for the [`web-stack-advisor`](../../.claude/skills/web-stack-advisor/SKILL.md) skill,
rather than a blog-claim demo like [`labeling-django/`](../labeling-django/README.md),
[`labeling-fastapi-react/`](../labeling-fastapi-react/README.md), or [`long-jobs/`](../long-jobs/README.md).
See [`demos/README.md`](../README.md) for how all four fit together, and
[`PLAN.md`](../../PLAN.md) (repo root) / [`PROMPT.md`](PROMPT.md) for the brief this was built from.

## The idea

The skill is ~530 lines of Markdown tables that a reader has to take on faith. This demo makes it
checkable instead: a static, no-backend interactive map of PSA International's container
terminals worldwide, built at **rung 1** of the skill's own five-rung ladder — static HTML + D3 +
Tailwind — because that is exactly what
[`references/use-cases.md`](../../.claude/skills/web-stack-advisor/references/use-cases.md)'s
"share a chart with teammates" row recommends for this use case (functions 1, 2, 3 only; no
server, no persistence, no auth).

The page then shows its own working, on the same scrolling page:

1. **The map** — the product itself: PSA's terminals, sized by designed capacity, cross-filtered
   with two companion charts.
2. **Why this stack** — a build-trail panel replaying the skill's 12-functionality verdict for
   *this app*, rendered from `data/advisor-model.json` and `data/this-app-verdict.json` rather
   than hardcoded into the HTML.
3. **Try the advisor** — a live version of the skill: pick one of its eight documented use cases,
   or answer its five intake questions yourself, and watch the same `js/advisor.js` logic derive a
   recommendation in front of you.

The point: **the skill's advice is a function you can run, not an opinion.** `js/advisor.js` is a
pure module encoding the skill's scoring rules, and `tests/advisor.test.js` asserts that every one
of the eight use cases `references/use-cases.md` documents still produces the stack that file
says it should — so this demo verifies the skill, rather than just displaying it.

## Stack, and why it's the stack

- **D3 v7**, ESM CDN import (`https://cdn.jsdelivr.net/npm/d3@7/+esm`), same route
  [`dataviz-python-js/d3-interactive-web/`](../../dataviz-python-js/d3-interactive-web/README.md)
  uses.
- **Tailwind 4 + daisyUI 5**, both CDN browser builds — the same no-Node, no-build-step route
  [`labeling-django/`](../labeling-django/README.md) verified, applied here to a page with no
  backend at all rather than Django templates. This is `references/use-cases.md`'s prescription
  for "business users, read-only": static D3 polished with a Tailwind kit (see link above).
- **`css/style.css`** holds only the `dataviz` skill's validated
  categorical palette as CSS custom properties (identical values to
  `d3-interactive-web/css/style.css`'s, light and dark, re-validated with
  `scripts/validate_palette.js` rather than assumed — see "Verification" below) plus this page's
  D3-specific marks. Tailwind/daisyUI own layout and off-the-shelf components; this file owns
  everything the chart code itself draws.
- **Zero npm dependencies, no build step.** `package.json` exists only for `"type": "module"` and
  the `node --test` test script.
- Served with the repo-root tooling: `npm run serve -- demos/psa-terminal-map`.

This demo deliberately does **not** read [`demos/sample-data/`](../sample-data/README.md) — that
fixture is the shared ticket-triage scenario for demos 1 and 2. This one has its own domain data.

## Data provenance

`data/terminals.json` covers PSA International's **deepsea container terminals only** — inland,
rail, and dry-port terminals are out of scope, and PSA's full footprint (70+ terminals across
180+ locations in 45 countries, counting those) is larger than what's in this file. Every record
carries a non-empty `sources: []` array of the URLs the figures were retrieved from and a
`retrievedDate`; any field PSA does not publish is `null`, never invented or estimated.
Coordinates are the terminal's approximate public location (`coordinatesApproximate: true`
throughout) — they position a dot on a map, not survey data.

**27 terminals across 17 countries and all five regions** made the cut: Southeast Asia (3),
Northeast Asia (8), Middle East/South Asia/Africa/Türkiye (4), Europe (6), Americas (6). Most
(20 of 27) came directly from PSA's own official per-terminal factsheet PDFs
(`globalpsa.com/wp-content/uploads/.../<TERMINAL-NAME>.pdf`, revision `2026.04.R1`), which carry
berths, quay length, depth, area, quay cranes, and designed capacity together in one table. The
remaining 7 (Tianjin Port Alliance, Mersin, Panama, and both Halifax terminals) rely on secondary
sources, since PSA's own factsheet either 404'd or doesn't exist for them — those have more `null`
fields on purpose, since only figures directly confirmed on a fetched page were kept, never a
number from an unconfirmed search-snippet summary.

Southeast Asia came up short (3 terminals) because PSA's genuinely-deepsea footprint there is
smaller than the other regions once inland/hinterland connectors are excluded — see below.
Several terminals that looked in-scope were deliberately left out rather than guessed at: SP-PSA
International Port (Vietnam, a bulk-cargo terminal, not container), PSA Zeebrugge (Belgium, a
RoRo/forest-products terminal), the Thai Connectivity Terminal (a Chao Phraya river/barge
connector, not deepsea), PSA Ameya (an inland container freight station), South Asia Gateway
Terminals in Colombo (no confirmed PSA ownership stake found), Hibiki (Kitakyushu) and Incheon
(no confirmed current PSA operational involvement or usable figures found), and Fuzhou's
terminals (PSA's own factsheet 404'd and secondary sources gave mutually contradictory figures
for the same terminal name — left out rather than pick one unverifiable version).

These are figures **as published by PSA and its terminals**, current as of the retrieval date
above (2026-09-24, against PSA's `2026.04.R1` factsheet revision) — they may already be stale by
the time you're reading this, and this is a demo dataset for showcasing the skill, not an
authoritative reference for PSA's actual network. The group-wide KPI figure
(`data/group-stats.json`) is PSA's own reported 2025 group throughput (105.0M TEU) from its
14 Jan 2026 press release — a distinct, separately-sourced statistic, not a sum of the
per-terminal designed capacities above (most of which are individual terminals' *designed*
capacity, not actual throughput, and several are `null`). The vendored `data/world-110m.json` is
world-atlas's 110m-resolution land topology (Natural Earth-derived, public domain), fetched once
rather than loaded from a CDN at runtime so the page works offline — see
[docs/javascript.md](../../docs/javascript.md)'s "Vendoring a third-party data file" for the
convention this follows.

**Spot-check.** Three records were picked at random and checked by hand against their cited PDF
by actually reading the fetched document (not just trusting its filename or metadata): Baltic
Hub, Dalian Container Terminal, and PSA Singapore. All three matched their source PDF exactly on
every field — berths, quay length, area, depth, quay cranes, and designed capacity.

## `js/advisor.js`: the skill's rules as data-driven logic

Two rule sets, applied in order, never mutating the caller's functionality-tick `Set`:

- **Rule C** ([`references/functionalities.md`](../../.claude/skills/web-stack-advisor/references/functionalities.md),
  "How to use the table"): ticks at 7-11 onward (persistence, forms, auth, authorization, session)
  push toward Django; functionality 4 alone is a FastAPI "demo a model"; functionality 3 + 6
  together is Streamlit (or Dash, when a `layoutControl` signal is set — see `references/use-cases.md`'s
  "Streamlit (Dash if you need layout control)"); anything lighter is static HTML + D3.
- **Rule D** (`references/use-cases.md`, "When to escalate a rung", linked above): three named
  escalations — Streamlit/Dash → Django (accounts with different data visibility), Flask/FastAPI →
  Django (re-implementing auth/ORM/admin), Django → React+API (an app-like UI, an external
  consumer, or a front-end engineer owning the UI) — plus the audience modifier
  (`references/use-cases.md`'s "Audience adjusts the pick" table), applied last.

Functionality 12 (background/long jobs) deliberately does **not** push toward Django on its own —
Django 6.0's own tasks API ships no worker
([`references/background-jobs.md`](../../.claude/skills/web-stack-advisor/references/background-jobs.md)) —
so a tick there surfaces as a flagged gap instead of changing the rung.

## Tests

`node --test` (Node v20.18.1 verified on this machine — the stable built-in runner has been
available since Node 18, so
[`d3-interactive-web/`](../../dataviz-python-js/d3-interactive-web/README.md)'s hand-rolled runner
isn't needed here; see [docs/javascript.md](../../docs/javascript.md)). Zero dependencies.

- **`tests/advisor.test.js`** — the load-bearing test: all eight of `references/use-cases.md`'s
  documented use cases (the "multi-user product prototype" case is split into two rows here, one
  functionality set with two documented outcomes depending on the app-like-UI flag) produce the
  stack that file documents; the 4+5 two-projects rule; all three Rule D escalation transitions;
  the audience modifier changing the pick without changing the functionality `Set` object passed
  in.
- **`tests/dataShape.test.js`** — every terminal has every required field, a non-empty sourced
  array of real URLs, in-range `[longitude, latitude]` coordinates, and every numeric field is
  either a positive number or explicitly `null`, never a placeholder string.

D3 rendering itself is checked by eye, per this repo's convention (see "Manual checks" below).

## Run it

```bash
# from the repo root
npm install                                  # once, if node_modules/ is absent
npm run serve -- demos/psa-terminal-map
```

Then open the URL `http-server` prints (e.g. http://localhost:8080). Opening `index.html` directly
via `file://` will not work — the page `fetch()`s its own JSON files, which browsers block over
`file://`; it needs a static server.

```bash
cd demos/psa-terminal-map
npm test
```

## Manual checks

1. The map renders with every terminal as a circle; hovering one shows a tooltip.
2. Clicking a terminal (on the map or the top-15 chart) opens the detail card with a working
   source link.
3. Clicking a region chip, or a bar on the region-capacity chart, filters the map and the top-15
   chart together; the chip and the bar both show the same selection.
4. Clearing the filter (Reset filters) restores every terminal.
5. The search box narrows all three (map, both charts) by terminal/country name.
6. Zoom/pan on the map works, and "Reset view" returns it to the initial framing.
7. Act 2's ladder highlights rung 1, and its rung-4/5 links open
   [`labeling-django/`](../labeling-django/README.md) and
   [`labeling-fastapi-react/`](../labeling-fastapi-react/README.md).
8. Act 3: clicking each of the eight use-case shortcuts produces a result; filling in the intake
   form and submitting produces a result from the same logic.
9. The page is legible at phone width and in dark mode (`prefers-color-scheme: dark`).

## Reproducing this demo

[`PROMPT.md`](PROMPT.md) is the build prompt this demo was implemented from, and [`PLAN.md`](../../PLAN.md)
(repo root) is the fuller planning brief it was written from — both kept for future reference.

## Out of scope

Deployment (this repo's `deploy/` material is unrelated; this demo is local-only), live PSA data
feeds, inland/rail terminals, and any backend. A live-throughput version of this map is the
skill's own escalation story: rung 3, a small API — see `js/advisor.js`'s escalation rules above,
and `data/this-app-verdict.json`'s `escalationTriggers`.
