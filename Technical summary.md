# Technical Summary

Reference notes for this repo: a hands-on working-through of **"Data
Visualization with Python & JavaScript"** by Kyran Dale. The book's
running example dataset is Nobel Prize winners; every stage here swaps
that for **Pokemon** instead, keeping the book's techniques and pipeline
shape intact. This file is the one-page map of what's been built, why
it's shaped the way it is, and how the pieces connect — the per-stage
`README.md` files remain the source of truth for detail.

## The pipeline, end to end

The book's core arc is: **get data onto disk → clean it → store it →
analyze/visualize it statically → serve it over HTTP → visualize it
interactively in the browser.** Each arrow below is a stage in this repo:

```
data-scrape  →  data-process  →  data-analysis  (static PNGs, matplotlib)
                      │
                      └────────→  data-serve  →  d3-interactive-web
                                  (Flask REST API)   (D3, in-browser)

data-read-write — a parallel branch off data-scrape's raw CSV,
                   exploring storage options (not part of the main pipeline)
```

Two "fundamentals" stages (`javascript-prototype`, `webdev101`) precede
the pipeline and correspond to the book's early chapters on JavaScript
and browser basics, before the data pipeline itself starts.

Every stage folder is self-contained with its own `README.md`, tests,
and (where applicable) generated output. `data-process`'s output
(`pokedex.json` + `images/`) is the one generated artifact committed to
the repo, since `data-serve` (and everything downstream of it) needs it
to run without first re-scraping two live websites.

## Stage-by-stage

### `javascript-prototype/` — JS fundamentals
Book topic: JavaScript's object model, contrasted with a language the
reader may already know. Implements the same `Animal`/`Dog` example
three ways: hand-rolled prototype chains (`prototype.js`), ES6
`class`/`extends` sugar over the same mechanism (`class-syntax.js`),
and Python's class-based MRO for contrast (`python_oop.py`). Core
takeaway: JS objects delegate through a live `[[Prototype]]` chain;
Python objects have a fixed `type` and a precomputed MRO tuple.

### `webdev101/` — HTML/CSS/SVG/Canvas fundamentals
Book topic: the building blocks a web page is made of, before any
data-visualization library gets involved. A single Pokedex-themed page
covering four techniques: jQuery-rendered content from a data array,
inline SVG (real DOM nodes, so CSS/SMIL can animate them), 2D canvas
animation (a raster surface redrawn every frame), and a hand-rolled
pseudo-3D wireframe cube (manual rotation + perspective projection,
demonstrating why 3D math is needed before ever reaching for WebGL).

### `data-scrape/` — acquiring the raw data
Book topic: getting data off the internet, several ways, so the
tradeoffs are visible side by side. Four layers on the same target
(PokeAPI + pokemondb.net): raw `requests`, `requests-cache` (transparent
response caching), `pokebase` (a purpose-built API client library), and
BeautifulSoup scraping (for data + artwork PokeAPI doesn't expose).
`pokemon_scrapy/` repeats the scrape as a proper Scrapy project (spider
+ item pipeline, politeness moved into settings). `compile_pokedex.py`
is the bulk pipeline: all 721 Gen 1–6 species, resumable, partial
failures logged per-row rather than dropping data, written to
`pokedex.csv` + `images/`.

**Key lesson carried forward:** prefer an API over scraping whenever
one exists; scraping is what's left for data no API has.

### `data-read-write/` — storage options (parallel branch)
Book topic: reading tabular data into program structures and persisting
it, several ways. Reads `pokemon.csv` (a separate, pre-existing flat
dataset — Gen 1–6 stats), reshapes each row into a nested dict (flat
stat columns → a `stats` sub-dict), round-trips it through JSON
(handling the date type gap JSON has), then stores/queries it three
ways: SQLAlchemy ORM directly (`models.py`), the lower-boilerplate
`dataset` library (`dataset_store.py`), and MongoDB via `pymongo`
(`mongo_store.py`, the only one that doesn't need to flatten `stats`).

**Key lesson carried forward:** this dataset is relational at heart —
the ORM's explicit schema is the most defensible real-world choice here;
`dataset` earns its keep for throwaway scripts; MongoDB earns its keep
only once records genuinely stop sharing a shape.

### `data-process/` — cleaning for the web
Book topic: turning collected-with-compromises raw data into one
consistent dataset a web page can consume without excuses. Fixes what
`compile_pokedex.py` deliberately left inconsistent: mixed casing
(PokeAPI slugs vs. pokemondb.net prose) unified via `humanize()`, two
unit systems collapsed to one (`height_m`/`weight_kg`), missing fields
backfilled from the other source where derivable, and every artwork
image resized + padded to a uniform 300×300 square
(`standardize_image()`). Output: `pokedex.json` (one record per Pokemon,
real JSON arrays for `types`/`abilities`) + `images/`.

### `data-analysis/` — static visualization
Book topic: matplotlib as the static-chart tool, before the book moves
on to interactive/web charting. Four saved PNGs answering distribution
questions about the cleaned dataset: Pokemon per type, per generation,
top abilities, and a log/log height-vs-weight scatter. Follows this
repo's `dataviz` design conventions: single flat color per chart (no
series to distinguish), direct value labels on every bar, muted chart
chrome. The scatter is deliberately *not* colored by type — 18 types is
past the ~8-hue ceiling a categorical palette can keep distinct.

### `data-serve/` — serving over HTTP
Book topic: exposing the processed dataset as a real REST API, the
bridge between the Python data side and the JavaScript visualization
side. One Flask app, one set of routes (`/api/meta`, `/api/pokemon`,
`/api/pokemon/<name>`, `/api/pokemon/<name>/artwork`), behind two
interchangeable backends built against the same repository interface:
`file` (in-memory dict + disk reads, no database) and `sqlite`
(Flask-SQLAlchemy, artwork stored as a BLOB column — shown as a learning
comparison, with the README noting why an object store/CDN is what a
real deployment would actually use for images). CORS is enabled on
`/api/*` since the D3 page and this API run on different localhost
ports.

### `d3-interactive-web/` — interactive visualization
Book topic: the payoff chapter — D3 driving an interactive page against
a live REST API, closing the full pipeline. One page: type/generation
filters, a clickable Pokemon grid, a mini-biography detail panel, and
four D3-drawn charts covering the same ground as `data-analysis`'s
PNGs, recomputed live. D3 is CDN-loaded as an ES module, no bundler.
Notable interactivity beyond the book's baseline: clicking a chart bar
sets the same filter state as the dropdowns (one source of truth), and
charts are deliberately wired to always summarize the *whole* dataset
rather than the current filter (see that stage's README for why).
Deliberately steps outside the `dataviz` skill's single-hue default for
the type chart and scatter (colored by Pokemon type — a fixed, widely
memorized domain convention), mitigated by never relying on color alone
(every colored mark is paired with text).

## Cross-cutting patterns worth remembering

- **Comparison over prescription.** Nearly every stage implements the
  same problem multiple ways on purpose (four ways to fetch data in
  `data-scrape`; three storage backends in `data-read-write`; two API
  backends in `data-serve`) and states, in its README, when you'd
  actually reach for each — not just that they all work.
- **Partial-failure tolerance in collection, strict cleaning after.**
  `compile_pokedex.py` never drops a row over one source failing;
  `process_pokedex.py` is where inconsistency actually gets resolved or
  a row gets excluded. Collection and cleaning are different concerns
  with different failure policies.
- **Generated output is reproducible, so it's gitignored — except the
  one thing downstream stages need to run out of the box**
  (`data-process/pokedex.json` + `images/`), which is committed
  specifically so a fresh clone can run `data-serve` without first
  re-scraping two live sites.
- **A repository/interface boundary, once there's more than one backend
  to compare.** `data-serve/app.py`'s routes only ever call a
  `repository` object — never a backend's storage directly — which is
  what makes the `file`/`sqlite` backends provably produce identical
  responses instead of just claiming to.
- **Color and comment conventions.** Charts default to single-hue
  unless there's a real identity dimension to encode (per the `dataviz`
  skill); code throughout is deliberately over-commented relative to
  production style, since the point of this repo is recalling *why*
  something is built a certain way, months later.

## Tech stack at a glance

| Concern | Choice |
|---|---|
| Data acquisition | `requests`, `requests-cache`, `pokebase`, BeautifulSoup, Scrapy |
| Data storage (exploration) | SQLAlchemy ORM, `dataset`, MongoDB (`pymongo`) |
| Data cleaning/imaging | Pillow |
| Static charting | matplotlib |
| Backend API | Flask, Flask-SQLAlchemy, Flask-Cors, SQLite |
| Frontend | Vanilla HTML/CSS/JS, jQuery (DOM stages), D3 v7 (CDN, visualization stages) |
| Python tooling | Python 3.11, single repo-root `.venv`, pip-tools (`requirements.in`/`.txt`), pytest |
| JS tooling | Per-stage `package.json` where needed; root `package.json` for shared `http-server` only |

## Running the full pipeline locally

```bash
# 1. Python env (once)
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
.venv/Scripts/python.exe -m piptools sync requirements.txt

# 2. Acquire + clean data (skippable — pokedex.json/images/ are committed)
python data-scrape/compile_pokedex.py      # ~45-60 min, resumable
python data-process/process_pokedex.py

# 3. Static charts
python data-analysis/main.py               # → data-analysis/charts/*.png

# 4. Serve the API (terminal 1)
python data-serve/app.py

# 5. Serve the interactive page (terminal 2)
npm install
npm run serve -- d3-interactive-web
```

Then open the URL `http-server` prints (typically
http://localhost:8080) for the interactive D3 Pokedex, or check
`data-analysis/charts/` for the static matplotlib equivalents.

## Where to look for more detail

Each stage's own `README.md` is the authoritative source — this file is
a map, not a replacement:

- [`javascript-prototype/README.md`](javascript-prototype/README.md)
- [`webdev101/README.md`](webdev101/README.md)
- [`data-scrape/README.md`](data-scrape/README.md)
- [`data-read-write/README.md`](data-read-write/README.md)
- [`data-process/README.md`](data-process/README.md)
- [`data-analysis/README.md`](data-analysis/README.md)
- [`data-serve/README.md`](data-serve/README.md)
- [`d3-interactive-web/README.md`](d3-interactive-web/README.md)
- [`docs/python-implementation.md`](docs/python-implementation.md) / [`docs/javascript.md`](docs/javascript.md) — language-level conventions
