# d3-interactive-web

A single interactive page that pulls together every earlier Pokedex
stage: it fetches [`data-serve`](../data-serve/README.md)'s REST API
with [D3](https://d3js.org/) (loaded from a CDN, no local install), and
lets you filter the dataset, click a Pokemon to see its mini-biography,
and explore four charts of the same shape
[`data-analysis`](../data-analysis/README.md) already produced as
static PNGs - just recomputed live and drawn with D3 instead of
matplotlib.

This is the first stage that only *reads* from the pipeline
(`data-scrape` → `data-process` → `data-serve`) rather than adding to
it - see "Why the REST API, not the JSON file directly" below for why
it's built this way.

## Running it

Two things need to be running at once, in two different terminals:

```bash
# Terminal 1: the API (from the repo root, with .venv active)
python data-serve/app.py

# Terminal 2: a static file server for this page (from the repo root)
npm install                      # once, if you haven't already
npm run serve -- d3-interactive-web
```

Then open the URL `http-server` prints (typically
http://localhost:8080). The page fetches from
`http://localhost:5000` (data-serve's default address) - if you started
`data-serve/app.py` with a different `PORT`, update `API_BASE` in
`js/api.js` to match.

If `data-serve/app.py` isn't running (or is unreachable), the page
shows an inline message telling you to start it - it doesn't fail
silently or show a blank page.

## What's on the page

- **Filters** (`#type-filter`, `#generation-filter`, Reset) - scope the
  Pokemon list below by calling data-serve's `?type=`/`?generation=`
  query parameters directly (`js/api.js`'s `fetchPokemon()`), the same
  filtering the API itself supports (see
  [data-serve/README.md](../data-serve/README.md#endpoints)).
- **Pokemon list** - a scrollable grid of small sprite cards for
  whatever the current filter shows. Click one to select it.
- **Mini-biography panel** - the selected Pokemon's full-resolution
  artwork (from data-serve's `/api/pokemon/<name>/artwork` endpoint,
  not the small sprite used in the list), name, species, types (each
  with a small type-colored dot), height/weight, and abilities.
- **Four charts** - Pokemon per type, Pokemon per generation, top 15
  abilities, and a height-vs-weight scatter (log/log). These always
  summarize the **whole** dataset, not the current filter - see "Why
  the charts ignore the filter" below. The type chart and scatter are
  colored by Pokemon type, and the generation chart by a 6-color
  categorical palette - see "Design notes (charts)" below for how far
  that pushes past the `dataviz` skill's usual single-hue default, and
  why.

## Interactivity, not just filters

Two extra ways to drive the app, beyond the dropdowns, since this
stage is specifically about what D3 makes easy once data is bound to
DOM elements:

- **Click a type or generation bar** in a chart to set that same
  filter (clicking the already-selected bar clears it again, same as
  Reset). The dropdown updates to match, so there's exactly one source
  of truth for "what's filtered" even though two different UI pieces
  can set it.
- **Click a point on the height-vs-weight scatter** to open that
  Pokemon's mini-biography, same as clicking its card in the list.

## Why the charts ignore the filter

Filters usually scope everything on a page below them, and the four
charts here start out looking like exactly that kind of dashboard - but
they're deliberately wired to always summarize `state.allPokemon` (the
one unfiltered fetch made at load), never `state.visiblePokemon` (what
the filter currently shows. See `js/app.js`.). Two reasons:

1. **They're the direct D3 successor to data-analysis's saved PNGs.**
   Those PNGs answer "how is the whole dataset distributed", a question
   that only makes sense against the whole dataset - a "Pokemon per
   type" chart that shrinks to one bar the moment you filter to Fire
   types stops answering that question.
2. **Charts and dropdowns both drive the same filter state**, per
   "Interactivity, not just filters" above. If clicking a bar *also*
   changed what that bar (and every other bar) plotted, clicking would
   feel like it was pulling the rug out from under itself instead of
   cleanly setting a filter.

`index.html`'s "charts-note" explains this in-page too, so it isn't a
surprise the first time someone clicks a bar and the list changes but
the chart doesn't.

## Why the REST API, not the JSON file directly

This page could have used `d3.json()` to read
`data-process/pokedex.json` straight off disk and skip `data-serve`
entirely - simpler to run (one static server, no Flask process, no
CORS setup). It goes through data-serve's API instead because that's
the more complete demonstration: every earlier stage in this pipeline
gets exercised by this one page (scrape → process → serve → visualize),
and it's a closer match to how you'd actually build a data-backed
front end - a browser talking to a REST API - than reading a build
artifact off the same disk it's running from.

The cost of that choice is CORS: this page is served from one origin
(`http-server`, typically `localhost:8080`) and data-serve's API is a
different one (`localhost:5000`), so the browser blocks the response
unless the server explicitly allows it. `data-serve/app.py` now wraps
its `/api/*` routes in `flask_cors.CORS(...)` for exactly this reason -
see that stage's README for the full explanation.

## Files

- `index.html` - page structure: filter row, browse section
  (list + detail panel), charts section.
- `css/style.css` - all styling, including the color palette as CSS
  custom properties on `.viz-root` (see "Design notes" below).
- `js/api.js` - the only module that calls `fetch()` - every other
  module gets Pokemon data handed to it as plain JS objects/arrays.
- `js/chartData.js` - pure aggregation functions (`countByType()`,
  `countByGeneration()`, `topAbilities()`), no D3/DOM - a direct port
  of `data-analysis/charts.py`'s `count_*`/`top_abilities` functions.
  This is the half that's unit-tested.
- `js/charts.js` - D3 rendering: turns `chartData.js`'s summaries into
  the four SVG charts, plus the shared tooltip and a rounded-rect path
  helper used by both bar orientations.
- `js/typeColors.js` - the fixed Pokemon-type-to-color mapping, used by
  the type chart, the scatter, and the detail panel's type badges.
- `js/typeLegend.js` - renders the `#type-legend` color-key row from
  `typeColors.js`, once at load.
- `js/filters.js` - populates and wires the two `<select>` filter
  controls.
- `js/pokemonList.js` - renders the scrollable card grid via a D3
  data-join keyed by Pokemon name.
- `js/detail.js` - renders the mini-biography panel.
- `js/app.js` - entry point: holds all app state (`allPokemon`,
  `visiblePokemon`, current filters, current selection), fetches from
  the API, and re-renders the other modules when state changes.
- `tests/chartData.test.js` - tests for `chartData.js`'s three pure
  functions against a small synthetic dataset (see "Testing" below for
  why this isn't `node --test`/Jest).
- `package.json` - `"type": "module"` only, so `node
  tests/chartData.test.js` can use `import`/`export` - no npm
  dependencies (D3 is CDN-only, per this stage's whole point).

## Why D3, not jQuery, for the DOM work

Per [docs/javascript.md](../docs/javascript.md), stages that touch the
DOM normally reach for jQuery - but that guide also carves out an
exception for a stage that's explicitly *about* a different DOM
mechanism (it names `javascript-prototype` as the existing example).
This stage exists specifically to practice D3's selection/data-join/
scale/axis model, so every DOM-touching module here
(`pokemonList.js`, `detail.js`, `filters.js`, `charts.js`) uses D3
throughout, including for plain form control wiring that jQuery would
normally handle - mixing the two would mean maintaining two different
"how do I update the DOM" mental models on one small page for no
benefit.

D3 itself is loaded from a CDN as an ES module
(`https://cdn.jsdelivr.net/npm/d3@7/+esm`) directly in each file that
needs it (`import * as d3 from "..."`), per this task's constraint of
no local D3 install - there's no bundler and no `node_modules` for D3
in this stage.

## Design notes (charts)

Built following this repo's `dataviz` design skill, including where
this stage deliberately steps outside its default single-hue
recommendation for the sake of a more colorful, more Pokedex-flavored
page:

- **Type chart and scatter are colored by Pokemon type** (`js/typeColors.js`),
  not a flat hue. This is a deliberate override of the skill's default
  "one series, one flat color" rule (which is what
  [`data-analysis`](../data-analysis/README.md#chart-design-notes)'s
  static PNGs still follow) *and* of its ~8-hue categorical safety
  ceiling (18 types, not 8) - justified because Pokemon type colors are
  a fixed, widely memorized domain convention the games themselves
  teach, not an arbitrary mapping invented for this chart. Run through
  the skill's own validator, this 18-color set actually **fails** the
  lightness-band and chroma-floor checks (a few types read as too light
  or too gray to trust as a sole identity signal) - the accepted
  mitigation is the skill's other hard rule, "never color alone": every
  colored mark here is always paired with its type name as text too
  (an axis tick, a tooltip, or the badge label), and the
  `#type-legend` row above the charts spells out all 18 swatches at
  once. See the long comment at the top of `js/typeColors.js` for the
  full reasoning.
- **Generation chart uses the skill's validated categorical palette**
  (`--series-1` through `--series-6` in `style.css`) instead - 6 bars is
  well inside the 8-slot ceiling the skill's palette was actually
  validated for, so this one *is* the skill's default recommendation,
  no override needed. Generation *N* always gets slot *N* (never
  reassigned based on what's filtered), per the skill's "color follows
  the entity, never its rank" rule.
- **Abilities chart stays single-hue** (`--series-1`, the same blue
  `data-analysis`'s PNGs use). Unlike type or generation, an ability
  has no natural identity dimension to color by - coloring bars by
  their own count would just re-encode what the bar's length already
  shows, which the skill explicitly rules out.
- **Selection is a stroke ring, not a fill swap.** Clicking a bar or
  scatter point adds an `is-selected` class that draws a 2px
  `--text-primary` ring around it (`style.css`), rather than
  recoloring it - so the selected mark keeps showing its type/generation
  color instead of losing its identity the moment it's selected.
- **Bars: 24px max thickness, rounded only at the data-end.** A type bar
  grown from the left rounds its right corners only; a generation
  column grown from the bottom rounds its top corners only - both via
  one shared `roundedRectPath()` helper in `charts.js` rather than two
  near-duplicate ones. Corner radius is clamped to half the bar's own
  (variable) dimension, so a bar for a small value can't produce a
  self-intersecting arc.
- **Direct value labels on every bar.** The general rule is to label
  sparingly, but that's about *multi-series* charts where a flood of
  numbers competes with several colors for attention - here each chart
  answers one question and it *is* the whole story, so a label per bar
  (15-18 of them) stays readable.
- **Scatter hit targets are bigger than the dots.** Each point is a
  visible 4px-radius mark plus an invisible, larger (12px-radius)
  circle layered on top that actually owns the hover/click handlers -
  a literal 4px dot is too small to reliably point at or tap.
- **Colors live in CSS custom properties, applied from JS per-datum
  where identity varies.** The flat-hue case (`.mark-bar { fill:
  var(--series-1); }`) lives entirely in `style.css`; the per-type and
  per-generation cases set `.style("fill", ...)` from `charts.js`
  because the color itself depends on which datum is being drawn, not
  a single fixed role - but the *value* each one resolves to is still
  a `var(--series-N)`/`typeColors.js` lookup, never a hex baked
  directly into a chart function, so a future dark-mode toggle (this
  page currently only follows the OS-level `prefers-color-scheme`,
  with no in-page switch) still only needs to touch `style.css`.

## Pokedex icon

The header (and the browser tab favicon) reuse the same inline
Pokeball SVG [`webdev101`](../webdev101/README.md) already draws in
its own header - copied in rather than redrawn, so every Pokedex-themed
stage in this repo shares one icon instead of each inventing its own.
See that stage's README for why it's inline SVG (not an `<img>`): being
real DOM nodes means the shapes could be restyled or animated with CSS
if a later stage wanted that, though this page keeps it static.

## Testing

`tests/chartData.test.js` covers the three pure aggregation functions
in `chartData.js` against a small synthetic dataset (independent of
whether `data-serve` is running), the same reasoning
[`data-analysis/tests/test_charts.py`](../data-analysis/tests/test_charts.py)
uses for its own synthetic fixture. `charts.js`'s D3 rendering isn't
unit-tested - an SVG's geometry isn't a meaningful assertion, so
opening `index.html` and looking at the charts is the real check, same
as this repo's other stages treat a demo script as the check for
wiring rather than for logic.

```bash
node d3-interactive-web/tests/chartData.test.js
# or: npm test --prefix d3-interactive-web
```

This uses a small hand-rolled runner (`assert` + a local `test()`
helper) instead of `node --test` or Jest: the Node installed for this
repo predates `node:test` (added in Node 18), and this stage
deliberately has no npm dependencies to add Jest as one of. If your
Node is 18+, `node --test tests` works too, since the test file itself
doesn't depend on which runner calls it.
