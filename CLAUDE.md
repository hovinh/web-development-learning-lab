# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git

**Never run `git commit` in this repo, even if asked to "commit" as part of a larger task — the user always commits themselves.** Stage or leave changes as needed and, if a commit message is wanted, provide the message text for the user to use.

## Repository purpose

This is a personal learning lab for web development, built by the user working through a book/curriculum topic by topic. The user directs Claude to implement each stage; Claude is not just writing production code, it is producing *teaching-quality* reference code the user can revisit later to recall how something works.

Structure, tooling, and conventions below reflect how the user wants the repo built out. Update this file as new books, stages, or tooling are added.

## Intended structure

- One top-level folder per **book**, not per stage — this repo works through multiple books over time, and each book gets its own folder so they don't pile up loose at the repo root. Currently: [`dataviz-python-js/`](dataviz-python-js/) for *Data Visualization with Python & JavaScript*, [`django-impatient/`](django-impatient/) for *Django 4 for the Impatient*, [`django-for-beginners/`](django-for-beginners/) for *Django for Beginners* (William Vincent), [`rest-apis-flask/`](rest-apis-flask/) for *Building REST APIs with Flask* (Kunal Relan), and [`angular-typescripts-beginner/`](angular-typescripts-beginner/) for *Beginning Angular with TypeScript* (Greg Lim), and [`react-hooks/`](react-hooks/) for *Beginning React with Hooks* (Greg Lim), and [`html-and-css/`](html-and-css/) for *HTML & CSS: Design and Build Websites* (Jon Duckett), and [`javascript-and-jquery/`](javascript-and-jquery/) for *JavaScript & jQuery: Interactive Front-End Web Development* (Jon Duckett).
- Inside a book folder, one subfolder per stage/topic of that book's curriculum (e.g. `dataviz-python-js/data-scrape/`, ...). Each stage is a self-contained unit — do not let later stages silently depend on earlier ones unless the book's material genuinely builds that way.
- `deploy/`, `docs/`, and `sandpit/` are top-level but are **not** book folders — they're cross-cutting and serve every book:
  - `deploy/` hosts `dataviz-python-js/data-serve`+`d3-interactive-web` (Render + GitHub Pages) and `django-impatient/moviereviews` (PythonAnywhere) on free public infrastructure rather than teaching a new topic. See [deploy/README.md](deploy/README.md) and [deploy/pythonanywhere.md](deploy/pythonanywhere.md).
  - `docs/` holds the language implementation guides (below), which apply to any book's Python/JS stages, not just one.
  - `sandpit/` is scratch space for quick, throwaway experiments, independent of whichever book is current.
- Each stage folder gets its own `README.md` explaining the idea and implementation for that stage, written so the user can come back months later and quickly recall *why* the code is shaped the way it is — not just what it does. Update a stage's README whenever its implementation changes.
- Languages are primarily Python and JavaScript, chosen per-stage based on what the book covers at that point (e.g. a Python-based scraping stage, a Node/JS frontend stage, a FastAPI backend stage).
- Python dependencies are managed with a single **repo-root** virtual environment (`.venv`), not one per stage or per book — see Python setup below. JS stages that need their own `package.json`/`node_modules` still work per-stage as needed.

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

`dataviz-python-js/data-serve` and `dataviz-python-js/d3-interactive-web` are additionally deployed to free public hosting (Render for the Flask API, GitHub Pages for the static page), auto-redeploying on every push to `main` that touches either. Config lives in `deploy/render.yaml` and `.github/workflows/deploy-frontend-pages.yml` (the latter must stay under `.github/workflows/` — GitHub requires that exact location). See [deploy/README.md](deploy/README.md) for the one-time setup and free-tier tradeoffs (spin-down cold starts, no persistent disk). When editing `data-serve/app.py` or `d3-interactive-web/js/api.js`, keep the module-level `app` object (gunicorn's import target) and the hostname-based `API_BASE` switch intact — both exist specifically for this deployment path.

`django-impatient/moviereviews` is separately deployed to PythonAnywhere — **manually, not auto-deploying on push** (PythonAnywhere has no free-tier equivalent to Render's Blueprints/GitHub Pages' Actions). See [deploy/pythonanywhere.md](deploy/pythonanywhere.md) for the full setup and redeploy steps. `moviereviews/settings.py`'s `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS`/secure-cookie settings read from environment variables (falling back to local-dev values when unset — never hardcode a "production" value into the fallback itself), and `django-impatient/moviereviews/requirements-pythonanywhere.txt` is a deliberately separate, minimal dependency list scoped to just this app (not the repo-root `requirements.txt`, which locks every stage in the monorepo). Keep both intact when editing that settings file or app's dependencies.

## Tooling scope (for tool recommendations and use-case discussions)

When the user asks "which tool for X" or wants a web-dev use case broken down, the toolkit in scope is:

- **Explored in this repo (code or notes):** HTML/CSS, JavaScript, jQuery, D3, React, Angular, Flask, Django, and the Python data stack.
- **In scope but not explored here — no stages will be added:** FastAPI, Tailwind CSS, Streamlit, Dash. Recommend them from general knowledge, and say so when doing it (the repo has no code to point at). Do not create stage folders for them unless the user asks.
- **Out of scope:** deployment/hosting choices (assume local deployment; that is the team's design decision). The existing `deploy/` material stays as-is but isn't part of recommendations.
- **Audience:** the user's readers are data-related roles (data scientists, analysts, data and ML engineers) learning web dev, but the *end users* of what they build are often business people with no web-dev knowledge — prefer options that look clean and standard out of the box.

The tool-choice guidance is also packaged as a reusable, portable skill at [`.claude/skills/web-stack-advisor/`](.claude/skills/web-stack-advisor/SKILL.md) (12 web functionalities, use-case mapping, UI kits, multi-user, background jobs, worked example, plus starter notes for FastAPI/Streamlit/Dash/Tailwind under `references/tools/`). Those tool notes were written from documentation and have not been run in this repo. Keep the skill and this section consistent, and re-verify its dated ("checked September 2026") facts before relying on them. Blog drafts live under `blog/` and follow [docs/blog-style.md](docs/blog-style.md); the user does not want em-dashes in blog posts.

## Keeping docs in sync

There are two overview docs, the language implementation guides, plus one per stage:

- `CLAUDE.md` (this file) — instructions for Claude Code instances.
- `README.md` (repo root) — the human-facing overview, mirrors this file's structural/tooling content.
- `docs/python-implementation.md` and `docs/javascript.md` — language-specific best practice guides, linked from both overview docs above.
- `<book>/<stage>/README.md` — one per stage folder, covering that stage's idea and implementation.

**Every code change that affects structure, setup, tooling, or conventions must update `CLAUDE.md`, the root `README.md`, and the relevant implementation guide together, plus the relevant stage `README.md` if a stage was added or changed.** Don't let these drift — a stale root doc defeats the point of this repo, which is to make prior work easy to recall.

**Exception: `django-impatient/`.** That book's `README.md` doubles as a running learning log (see [django-impatient/README.md](django-impatient/README.md)'s "Log" section), updated as the user progresses through the material. Routine additions to that log stay inside `django-impatient/README.md` only — they don't need matching edits to this file, the root `README.md`, or `docs/python-implementation.md`. Only touch the outer docs for `django-impatient/` if something genuinely structural changes (e.g. a new dependency, a new top-level tool, a change to how the stage is run).
