# Web Development Learning Lab

A personal, hands-on lab for working through a web development curriculum/book, one stage at a time. Each stage lives in its own top-level folder with a self-contained implementation and a README explaining what it does and why.

> This is a learning repo, not a production codebase — code favors clarity and heavy comments over cleverness, so it's easy to come back to later and remember how things work.

## Structure

- One top-level folder per **book** — this lab works through more than one book over time, so each gets its own folder rather than piling all their stages loose at the repo root.
- Inside a book folder, one subfolder per stage/topic of that book's curriculum. Stages are self-contained; a later stage only depends on an earlier one if the book's material genuinely builds that way.
- Each stage folder has its own `README.md` explaining the idea and implementation for that stage — that's the place to look for details on any specific topic.
- Languages are primarily Python and JavaScript, chosen per stage based on what the curriculum covers at that point.
- `deploy/`, `docs/`, and `sandpit/` are top-level too, but aren't book folders — they're cross-cutting and serve every book (deployment config, language guides, and scratch space respectively).

Books so far:

- [`dataviz-python-js/`](dataviz-python-js/) — *Data Visualization with Python & JavaScript* (see [dataviz-python-js/Technical summary.md](dataviz-python-js/Technical%20summary.md) for the pipeline overview):
  - [`javascript-prototype/`](dataviz-python-js/javascript-prototype/README.md) — JS prototypal inheritance vs Python class-based OOP.
  - [`data-read-write/`](dataviz-python-js/data-read-write/README.md) — reading a CSV dataset, reshaping it, and round-tripping it through JSON.
  - [`data-scrape/`](dataviz-python-js/data-scrape/README.md) — fetching Pokemon data via a REST API, `requests-cache`, a client library, and BeautifulSoup scraping (with image download); a Scrapy spider+pipeline version of the scrape; and a bulk pipeline compiling all Gen 1-6 Pokemon into one CSV with artwork.
  - [`data-process/`](dataviz-python-js/data-process/README.md) — cleaning `data-scrape`'s raw CSV into one standardized JSON dataset + uniformly-sized images, ready for a web page to consume.
  - [`data-analysis/`](dataviz-python-js/data-analysis/README.md) — charting `data-process`'s dataset into saved PNGs (type/generation/ability distributions, a height-vs-weight scatter).
  - [`data-serve/`](dataviz-python-js/data-serve/README.md) — serving `data-process`'s dataset as a REST API via Flask, with interchangeable file/SQLite backends and Python + JS smoke-test scripts.
  - [`d3-interactive-web/`](dataviz-python-js/d3-interactive-web/README.md) — an interactive Pokedex page (D3, via CDN) that consumes `data-serve`'s REST API: filter by type/generation, click a Pokemon for its mini-biography, and four D3-drawn charts covering the same ground as `data-analysis`'s saved PNGs.
  - [`webdev101/`](dataviz-python-js/webdev101/README.md) — HTML/CSS/SVG/Canvas fundamentals via a Pokedex home page demo.
- [`django-impatient/`](django-impatient/README.md) — *Django 4 for the Impatient*: Django fundamentals via a `moviereviews` project; that README doubles as a running learning log.
- [`django-for-beginners/`](django-for-beginners/README.md) — *Django for Beginners* (William Vincent): Django fundamentals (URLs/Views/Models/Templates flow) via a separate small project per chapter.
  - [`pages/`](django-for-beginners/pages/) — first project (`django_project` + `pages` app): URLs/views/templates without a database.
  - [`message-board/`](django-for-beginners/message-board/README.md) — second project (`django_project` + `message_board` app): a `Post` model (just `text`) listed on the homepage, seeded via a `seed_posts` management command, editable through Django's built-in admin site.
- [`rest-apis-flask/`](rest-apis-flask/README.md) — *Building REST APIs with Flask* (Kunal Relan):
  - [`hello-world/`](rest-apis-flask/hello-world/README.md) — smallest possible Flask app: one route, one plain-text response.
  - [`library-crud/`](rest-apis-flask/library-crud/README.md) — full CRUD REST API for `Author`/`Book` (one-to-many), using Flask-SQLAlchemy and Marshmallow together.
- [`angular-typescripts-beginner/`](angular-typescripts-beginner/README.md) — *Beginning Angular with TypeScript* (Greg Lim):
  - [`my-app/`](angular-typescripts-beginner/my-app/README.md) — first Angular CLI project: `ng new` through `ng serve --open`, a `ProductComponent` mock landing page, and a `RatingComponent` (Bootstrap) demoing property/class/style/event/two-way binding.
- [`react-hooks/`](react-hooks/README.md) — *Beginning React with Hooks* (Greg Lim): concept notes (components, props/state/events, conditional rendering, forms with hooks, persisting data through a REST API); no stage projects yet.
- [`html-and-css/`](html-and-css/README.md) — *HTML & CSS: Design and Build Websites* (Jon Duckett): concept notes (HTML structure/text/lists/links/images/tables/forms, CSS selectors/box model/layout, site design); no stage projects yet.

Cross-cutting, not book folders:

- [`sandpit/`](sandpit/README.md) — scratch area for quick, throwaway experiments (not a curriculum stage).
- [`deploy/`](deploy/README.md) — puts `dataviz-python-js/data-serve`+`d3-interactive-web` (Render + GitHub Pages, auto-deploying on every push) and `django-impatient/moviereviews` ([PythonAnywhere](deploy/pythonanywhere.md), manual redeploy) on free public hosting.

## Python setup

Python dependencies for all stages share a single virtual environment at the repo root, managed with [pip-tools](https://github.com/jazzband/pip-tools).

```bash
# Create the venv (Python 3.11)
py -3.11 -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1   # PowerShell
source .venv/Scripts/activate  # bash

# Add a dependency: edit requirements.in, then compile the lockfile
.venv/Scripts/python.exe -m piptools compile requirements.in -o requirements.txt

# Install/sync the venv to match the lockfile exactly
.venv/Scripts/python.exe -m piptools sync requirements.txt
```

- Direct dependencies go in `requirements.in`.
- `requirements.txt` is generated — never edit it by hand.

## JavaScript setup

JS stages manage their own `package.json` and dependencies locally within their stage folder. The one exception is the repo-root `package.json`, which holds shared dev tooling that isn't specific to any single stage — currently just [`http-server`](https://github.com/http-party/http-server), a zero-config static file server, for previewing any stage's plain HTML/CSS/JS pages without Python's `http.server`.

```bash
# Install (from the repo root)
npm install

# Serve a stage's folder (defaults to port 8080)
npm run serve -- dataviz-python-js/webdev101

# Pass through any http-server flag after --, e.g. a different port
npm run serve -- webdev101 -p 8081
```

Then open the URL `http-server` prints (e.g. http://localhost:8080). Commit the root `package.json`/`package-lock.json`; `node_modules/` is gitignored, same as any stage's.

## Deployment

`dataviz-python-js/data-serve` and `dataviz-python-js/d3-interactive-web` are also live on free public
hosting, kept in sync with `main` automatically:

- **Live page**: https://hovinh.github.io/web-development-learning-lab/
- **Live API**: https://pokedex-learning-lab-api.onrender.com/api/meta

See [deploy/README.md](deploy/README.md) for the setup and the two
platforms involved (Render for the API, GitHub Pages for the static
page). The API is on Render's free tier, so it spins down after 15
minutes idle — the first request after a quiet spell takes ~30-50s to
wake it back up.

`django-impatient/moviereviews` is separately deployed to
[PythonAnywhere](https://www.pythonanywhere.com/) — see
[deploy/pythonanywhere.md](deploy/pythonanywhere.md). Unlike the two
above, this one has no auto-deploy on push (PythonAnywhere's free tier
has no equivalent to Render's Blueprints or GitHub Pages' Actions), so
redeploying a change means following that guide's steps by hand each
time.

## Implementation guides

For language-specific best practice (project layout, style, formatting/linting, testing), see:

- [docs/python-implementation.md](docs/python-implementation.md)
- [docs/javascript.md](docs/javascript.md)

## Contributing to this repo (for future edits)

This repo also has a [CLAUDE.md](CLAUDE.md) with the same structural/tooling info, written for Claude Code. **Keep this README, CLAUDE.md, and the implementation guides in sync** — any change to the repo's structure, setup, or conventions should be reflected across all of them.
