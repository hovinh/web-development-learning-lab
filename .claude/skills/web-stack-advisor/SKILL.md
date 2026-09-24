---
name: web-stack-advisor
description: >-
  Recommend the lightest web tooling for a data professional's use case (data scientist, analyst, data or ML engineer): share a chart, explore data, serve a model, labeling tool, dashboard, multi-user product prototype. Breaks the use case into 12 web functionalities (styling, interactivity, API, persistence, auth, background jobs and more) and maps each to a tool. Use when the user asks "what should I build this with", "Streamlit or Dash or Flask or FastAPI or Django or React", or describes an app idea for a demo, data exploration or product prototype.
---

# Web stack advisor

Help people who work with data (data scientists, analysts, data and ML engineers) pick web
tooling without drowning in options.
The method is: **decompose the use case into functionalities, pick the lightest tool
that covers each, and flag what is missing.** Do not start from a favourite framework.

## Scope defaults (override if the project's CLAUDE.md says otherwise)

- **Local deployment only.** Hosting and deployment are the team's decision. Do not
  recommend hosts. If the end users are non-technical, do mention that "runs on my
  laptop" is a limit, then stop there.
- **Toolkit in scope:** HTML/CSS, JavaScript, jQuery, D3, React, Angular, Flask,
  FastAPI, Django, Streamlit, Dash, Tailwind CSS, and the Python data stack.
- **Two audiences.** The *builder* is a data professional (comfortable with Python,
  values dev speed). The *end user* is often a business person with no web knowledge (values a
  clean, standard-looking, self-explanatory UI). Ask which one the tool is for.

## Procedure

1. **Ask (only what is not already clear):**
   - Who uses it: peers, or business users?
   - One user or many? Do they log in? Do they see different data?
   - Does it save anything (persistence), or only display?
   - Does any step take longer than a few seconds?
   - Does another system need to call it (API)?
2. **Decompose** into the 12 functionalities below. Mark which ones the use case needs.
3. **Pick the lightest tool per functionality**, then collapse to as few tools as
   possible (one framework covering many functions beats a stack of specialists).
4. **Flag gaps and risks** (multi-user, background jobs, Windows limits, unverified
   tools). Say plainly when a recommendation comes from general knowledge rather than
   from something that was actually built and run.
5. **Offer the next step:** a minimal starter, or a comparison for their exact case.
   `references/worked-example-labeling-tool.md` is a model comparison.

## The lightest-first ladder

1. **Static HTML + D3** (+ Tailwind): show a finished result. No server.
2. **Streamlit or Dash**: explore data, or a tool for peers. Python only, no JS.
3. **Flask or FastAPI**: serve a model or data over HTTP.
4. **Django (+ Tailwind kit)**: users, database, forms, admin. A multi-user prototype.
5. **React (or Angular) + Tailwind over an API**: only when the UI is genuinely
   app-like (instant updates, keyboard-driven, complex client state).

Tailwind is orthogonal: it only does styling and works with every rung.
React and Angular are the same tier; for a solo data professional, React is the better default
(lighter start, bigger ecosystem). Angular's strength is opinionated structure for
large teams.

## The 12 functionalities (short form; detail in `references/functionalities.md`)

| # | Functionality | Lightest tool |
|---|---|---|
| 1 | Presentation (static content) | HTML/CSS |
| 2 | Styling and layout | Tailwind + a component kit (`references/ui-kits.md`) |
| 3 | Client interactivity | D3/JS; React if state is complex; Streamlit/Dash to skip JS |
| 4 | API: providing | FastAPI (typed, auto docs) or Flask |
| 5 | API: consuming | `fetch` in JS, React, Angular |
| 6 | Server-side compute | Flask/FastAPI/Django, or Streamlit/Dash |
| 7 | Persistence | Django ORM; SQLAlchemy with Flask/FastAPI; SQLite locally |
| 8 | Forms and CRUD | Django (forms + admin) |
| 9 | Authentication | Django built-in; Streamlit `st.login` (OIDC); others need add-ons |
| 10 | Authorization | Django permissions; the rest hand-rolled (`references/multi-user.md`) |
| 11 | Session and state | Django sessions, Streamlit `session_state`, React state |
| 12 | Background and long jobs | `references/background-jobs.md` |

## Quick picks by use case (detail in `references/use-cases.md`)

| Use case | Pick |
|---|---|
| Share a finished chart | Static HTML + D3 |
| Explore a dataset | Streamlit (Dash if you need layout control) |
| Peer dashboard | Dash or Streamlit |
| Demo a model | FastAPI (its `/docs` page is a free UI) + optional Streamlit page |
| Labeling / review tool | Django (the admin is often enough) |
| Multi-user product prototype | Django + Tailwind kit; React + shadcn/ui over an API if the UI is app-like |
| Pipeline that ends in a page | Python writes JSON, static D3 renders it |
| Throwaway experiment | Plain HTML/JS, no build |

## Cautions

- **Authorization must be enforced on the server.** Hiding a button in React is not
  security.
- Per-tool notes with starter code live in `references/tools/`. Their status differs, and
  each file states its own at the top: **FastAPI and Tailwind were verified by building
  and running them**, while **Streamlit and Dash were written from documentation and
  general knowledge only**. Say which of the two you are relying on, and check current
  docs for anything time-sensitive.
- **This skill is self-contained and ships no code.** Where a note cites a `demos/...`
  path, that is a demo in the skill's source repo, not a folder in the project you are
  installed into:
  <https://github.com/hovinh/web-development-learning-lab/tree/main/demos>.
  Cite those as evidence that a claim was tested; do not tell the user to open the path
  locally, and do not assume the files exist here.
- Time-sensitive facts below were checked in **September 2026**. Re-check before
  repeating them later:
  - Streamlit has built-in OIDC login (`st.login`, `st.user`), but no roles.
  - `dash-auth` is HTTP Basic Auth only (no logout button).
  - `fastapi-users` is in maintenance mode (security fixes only).
  - Django 6.0 ships a tasks API (`django.tasks`) but **no worker** and no retries or
    scheduling; you still need a backend such as Celery or a database-backed one.
  - FastAPI `BackgroundTasks` runs in the web process, with no persistence or retries.
  - RQ needs `os.fork` (no native Windows; WSL required). Celery has dropped Windows
    support (the `solo` pool is a dev-only workaround). Huey can use SQLite storage.
  - Tailwind has a standalone CLI that needs no Node.js (also `pip install pytailwindcss`).

## Reference index

- `references/functionalities.md`: the 12 functionalities in full
- `references/use-cases.md`: use cases as combinations of functionalities
- `references/ui-kits.md`: getting a pretty but standard UI
- `references/multi-user.md`: what "multi-user" means and per-tool support
- `references/background-jobs.md`: long-running jobs, tools, Windows notes
- `references/worked-example-labeling-tool.md`: Django vs FastAPI + React comparison
- `references/tools/fastapi.md`, `streamlit.md`, `dash.md`, `tailwind.md`
