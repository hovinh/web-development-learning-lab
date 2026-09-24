# Use cases as combinations of functionalities

Numbers refer to `functionalities.md`.

| Use case | Functions needed | Recommended stack | Why |
|---|---|---|---|
| Share a chart with teammates [^1] | 1, 2, 3 | Static HTML + D3 (+ Tailwind) | No server to run; the data ships as JSON/CSV |
| Explore a dataset | 3, 6 | Streamlit first; D3 only for custom visuals | Fastest path from a DataFrame to widgets |
| Metrics dashboard for peers | 3, 6, maybe 9 | Dash | More layout and callback control than Streamlit |
| Demo a model | 4, 6 | FastAPI, plus a Streamlit page if a UI is wanted | `/docs` gives a free interactive form |
| Labeling or review tool | 7, 8, 9, 10 | Django | Forms, auth, admin and ownership filtering are solved |
| Multi-user product prototype | 2 to 11 | Django + Tailwind kit; React + shadcn/ui over an API if the UI is app-like | One project vs two |
| Pipeline that ends in a page | data stages, 1, 3 | Python writes JSON, static D3 renders it | Nothing live to keep running |
| Throwaway experiment | 1, 3 | Plain HTML/JS | No build, no dependencies |

## Audience adjusts the pick

| Who uses it | Lean toward |
|---|---|
| Fellow data people (DS, analysts, DE) | Streamlit, Dash, FastAPI `/docs` |
| Business users, read-only | Static D3 or Dash, polished with a Tailwind kit |
| Business users, interactive with accounts | Django + Tailwind kit, or React + shadcn/ui |

Business users judge by look and polish, not architecture. A raw Streamlit page can
be fine for a peer and look unfinished to a manager.

## When to escalate a rung

- Streamlit/Dash to Django: you need accounts with different data visibility, saved
  records, or a back-office screen.
- Flask/FastAPI to Django: you are re-implementing auth, an ORM layer and an admin.
- Django to React + API: the UI needs instant, app-like interaction, or other systems
  also need the API, or a front-end engineer will own the UI. Django can grow into this
  later by adding Django REST Framework; the data model survives.

[^1]: **Status: verified by running**, and by a test suite. In the skill's source repo (link in
    `SKILL.md`; not a folder in this project): `demos/psa-terminal-map/` is a static HTML + D3 +
    Tailwind page built specifically at this row's recommended rung, and it renders this skill's
    own functionality table and ladder as its build trail. Its `tests/advisor.test.js` asserts
    that all eight use cases in this file, including this one, produce the stack documented here
    - not just this row, but every row above.
