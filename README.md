# Web Development Learning Lab

A personal, hands-on lab for working through a web development curriculum/book, one stage at a time. Each stage lives in its own top-level folder with a self-contained implementation and a README explaining what it does and why.

> This is a learning repo, not a production codebase — code favors clarity and heavy comments over cleverness, so it's easy to come back to later and remember how things work.

## Structure

- One top-level folder per stage/topic (e.g. `web-scraping/`, `fastapi-backend/`, ...). Stages are self-contained; a later stage only depends on an earlier one if the book's material genuinely builds that way.
- Each stage folder has its own `README.md` explaining the idea and implementation for that stage — that's the place to look for details on any specific topic.
- Languages are primarily Python and JavaScript, chosen per stage based on what the curriculum covers at that point.

Stages so far:

- [`javascript-prototype/`](javascript-prototype/README.md) — JS prototypal inheritance vs Python class-based OOP.
- [`data-read-write/`](data-read-write/README.md) — reading a CSV dataset, reshaping it, and round-tripping it through JSON.
- [`data-scrape/`](data-scrape/README.md) — fetching Pokemon data via a REST API, `requests-cache`, a client library, and BeautifulSoup scraping (with image download); a Scrapy spider+pipeline version of the scrape; and a bulk pipeline compiling all Gen 1-6 Pokemon into one CSV with artwork.
- [`data-process/`](data-process/README.md) — cleaning `data-scrape`'s raw CSV into one standardized JSON dataset + uniformly-sized images, ready for a web page to consume.
- [`data-analysis/`](data-analysis/README.md) — charting `data-process`'s dataset into saved PNGs (type/generation/ability distributions, a height-vs-weight scatter).
- [`data-serve/`](data-serve/README.md) — serving `data-process`'s dataset as a REST API via Flask, with interchangeable file/SQLite backends and Python + JS smoke-test scripts.
- [`webdev101/`](webdev101/README.md) — HTML/CSS/SVG/Canvas fundamentals via a Pokedex home page demo.
- [`sandpit/`](sandpit/README.md) — scratch area for quick, throwaway experiments (not a curriculum stage).

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
npm run serve -- webdev101

# Pass through any http-server flag after --, e.g. a different port
npm run serve -- webdev101 -p 8081
```

Then open the URL `http-server` prints (e.g. http://localhost:8080). Commit the root `package.json`/`package-lock.json`; `node_modules/` is gitignored, same as any stage's.

## Implementation guides

For language-specific best practice (project layout, style, formatting/linting, testing), see:

- [docs/python-implementation.md](docs/python-implementation.md)
- [docs/javascript.md](docs/javascript.md)

## Contributing to this repo (for future edits)

This repo also has a [CLAUDE.md](CLAUDE.md) with the same structural/tooling info, written for Claude Code. **Keep this README, CLAUDE.md, and the implementation guides in sync** — any change to the repo's structure, setup, or conventions should be reflected across all of them.
