# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a personal learning lab for web development, built by the user working through a book/curriculum topic by topic. The user directs Claude to implement each stage; Claude is not just writing production code, it is producing *teaching-quality* reference code the user can revisit later to recall how something works.

The repo is a fresh scaffold — as of now it contains only a `LICENSE` file. Structure, tooling, and conventions below reflect how the user wants the repo built out, not how it currently exists. Update this file as real folders and tooling are added.

## Intended structure

- One top-level folder per stage/topic of the curriculum (e.g. `web-scraping/`, `fastapi-backend/`, ...). Each stage is a self-contained unit — do not let later stages silently depend on earlier ones unless the book's material genuinely builds that way.
- `deploy/` is the one top-level folder that isn't a curriculum stage — it hosts `data-serve`/`d3-interactive-web` on free public infrastructure (Render + GitHub Pages) rather than teaching a new topic. See [deploy/README.md](deploy/README.md).
- Each stage folder gets its own `README.md` explaining the idea and implementation for that stage, written so the user can come back months later and quickly recall *why* the code is shaped the way it is — not just what it does. Update a stage's README whenever its implementation changes.
- Languages are primarily Python and JavaScript, chosen per-stage based on what the book covers at that point (e.g. a Python-based scraping stage, a Node/JS frontend stage, a FastAPI backend stage).
- Python dependencies are managed with a single **repo-root** virtual environment (`.venv`), not one per stage — see Python setup below. JS stages that need their own `package.json`/`node_modules` still work per-stage as needed.

## Python setup

- One shared virtual environment lives at the repo root: `.venv` (Python 3.11, created via `py -3.11 -m venv .venv`). Activate it before running any Python stage code.
  - PowerShell: `.venv\Scripts\Activate.ps1`
  - Bash: `source .venv/Scripts/activate`
- Dependencies are managed with **pip-tools**:
  - Add direct dependencies to `requirements.in` (top-level only, unpinned).
  - Compile the pinned, transitive lockfile with: `.venv/Scripts/python.exe -m piptools compile requirements.in -o requirements.txt`
  - Install/sync the venv to exactly match the lockfile with: `.venv/Scripts/python.exe -m piptools sync requirements.txt`
  - Never hand-edit `requirements.txt` — it's generated. Never `pip install` directly into `.venv` without also adding the package to `requirements.in` and recompiling, or the lockfile will drift.
- `.venv/` is gitignored; `requirements.in` and `requirements.txt` are committed.

## JavaScript setup

- Each JS stage manages its own `package.json`/dependencies inside its own folder — no shared root-level `node_modules` for stage code (see [docs/javascript.md](docs/javascript.md)).
- The one exception is the repo-root `package.json`: shared dev tooling that isn't specific to any stage, not a stage itself. Currently just [`http-server`](https://github.com/http-party/http-server) (`npm install`, then `npm run serve -- <stage-folder>`) for previewing a stage's static HTML/CSS/JS without Python's `http.server`. Add future repo-wide (not per-stage) JS tooling here the same way.
- `node_modules/` is gitignored at any depth; `package.json`/`package-lock.json` (root or per-stage) are committed.

## Coding conventions for this repo

- Audience is a beginner following along with a book — code should be structured according to best practice for the relevant framework/language, but kept easy to follow.
- Unlike typical production guidance, **do not be shy about comments here** — over-commenting is preferred so the user can understand *why* each piece exists when reviewing later, not just what it does.
- Prefer clarity and explicitness over clever abstractions, even where a terser production idiom exists — the point is for the user to learn the mechanics.
- Language-specific best practice is documented in full in the implementation guides below — follow them when writing Python or JavaScript code in any stage.

## Implementation guides

- [docs/python-implementation.md](docs/python-implementation.md) — project layout, style, formatting/linting, and testing conventions for Python stages.
- [docs/javascript.md](docs/javascript.md) — project layout, style, formatting/linting, and testing conventions for JavaScript stages.

## Deployment

`data-serve` and `d3-interactive-web` are additionally deployed to free public hosting (Render for the Flask API, GitHub Pages for the static page), auto-redeploying on every push to `main` that touches either. Config lives in `deploy/render.yaml` and `.github/workflows/deploy-frontend-pages.yml` (the latter must stay under `.github/workflows/` — GitHub requires that exact location). See [deploy/README.md](deploy/README.md) for the one-time setup and free-tier tradeoffs (spin-down cold starts, no persistent disk). When editing `data-serve/app.py` or `d3-interactive-web/js/api.js`, keep the module-level `app` object (gunicorn's import target) and the hostname-based `API_BASE` switch intact — both exist specifically for this deployment path.

## Keeping docs in sync

There are two overview docs, the language implementation guides, plus one per stage:

- `CLAUDE.md` (this file) — instructions for Claude Code instances.
- `README.md` (repo root) — the human-facing overview, mirrors this file's structural/tooling content.
- `docs/python-implementation.md` and `docs/javascript.md` — language-specific best practice guides, linked from both overview docs above.
- `<stage>/README.md` — one per stage folder, covering that stage's idea and implementation.

**Every code change that affects structure, setup, tooling, or conventions must update `CLAUDE.md`, the root `README.md`, and the relevant implementation guide together, plus the relevant stage `README.md` if a stage was added or changed.** Don't let these drift — a stale root doc defeats the point of this repo, which is to make prior work easy to recall.
