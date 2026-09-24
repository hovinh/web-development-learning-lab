# Demo 2 — labeling tool, FastAPI + React

Backs the blog's ["Two Real Stacks, One Problem"](../../blog/web-dev-for-data-people/2026-09-20-web-dev-for-data-people.md)
section and the `web-stack-advisor` skill's
[`worked-example-labeling-tool.md`](../../.claude/skills/web-stack-advisor/references/worked-example-labeling-tool.md).
Head-to-head counterpart to [`../labeling-django/`](../labeling-django/README.md) — same task,
same [shared sample data](../sample-data/README.md), same three users, same ownership rule. Where
Demo 1 is one project and one process, this demo is **two projects and two processes**
([`api/`](api/), [`web/`](web/)) — that split is itself one of the things the blog's comparison
is about.

## Auth: hand-built, and the exhibit

[`api/security.py`](api/security.py) and [`api/deps.py`](api/deps.py) implement the OAuth2-password
+ JWT pattern straight from [FastAPI's own docs](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/):
hash and verify passwords with `pwdlib` (Argon2), mint and verify JWTs with `PyJWT`, and rebuild
"who is this request from" on every single call via `deps.get_current_user`. That's the whole
count against Django's `django.contrib.auth`, which gives
[`../labeling-django/`](../labeling-django/README.md) the equivalent behavior by installing an
app that's already in `INSTALLED_APPS` by default — zero lines like these.

## Ownership: a shared dependency, not a queryset

The blog's honest version of "a check in every endpoint": `deps.py`'s `get_owned_item` is the one
shared ownership check the `web-stack-advisor` skill recommends ("put the ownership filter in one
place"). But sharing the *code* doesn't make the *check* automatic the way Django's queryset
filter does. Counting `api/main.py`'s routes:

| Route | How ownership is enforced |
|---|---|
| `GET /items/{item_id}` | `Depends(deps.get_owned_item)` |
| `POST /items/{item_id}/label` | `Depends(deps.get_owned_item)` |
| `GET /items` (the queue list) | its own inline `.filter(Item.assigned_to_id == current_user.id)` — a list endpoint can't reuse a single-item dependency, so this is a **third**, separately-written place the same rule has to be remembered |

Three routes, three places the rule has to be remembered — two of them sharing a function, one
of them not, and nothing in FastAPI stops a fourth route from being added tomorrow without
`Depends(get_owned_item)` at all. Compare `../labeling-django/labeling/views.py`'s single
`Item.objects.filter(assigned_to=request.user)` line, which makes writing an *unfiltered* query
the unusual, easy-to-notice thing instead.

## Admin: you build it

`api/main.py`'s `GET /admin/labels` (gated by `deps.require_admin`) is the hand-built equivalent
of opening `../labeling-django/`'s `/admin/` and seeing every reviewer's labels for free. There's
no React page for it — deliberately: building one would just be more code demonstrating the same
point `../labeling-django/labeling/admin.py`'s two `@admin.register` calls already make for free.
Exercise it through FastAPI's own generated `/docs` instead — see "Manual checks" below.

## Interactivity: the actual payoff

Everything above is more code than the Django demo needs for the same guarantees. What this stack
buys back: [`web/src/components/LabelPanel.jsx`](web/src/components/LabelPanel.jsx) binds `1`/`2`/`3`
keys straight to Correct/Incorrect/Unsure, and [`web/src/App.jsx`](web/src/App.jsx) auto-advances
to the next unlabeled item after each submit — no page reload, no click required to move on. This
is normally out of scope at this repo's teaching-minimal depth, but it's the specific thing the
blog names as the reason to climb to this stack in the first place, so it earns its place here.

## Styling

`web/vite.config.js` uses `@tailwindcss/vite`, Tailwind 4's official Vite plugin — it scans the
React source at dev/build time and ships only the utility classes actually used. Contrast
`../labeling-django/`'s CDN browser build, which recompiles Tailwind's entire utility set on every
page load with no purge step; that's the "no Node, no build step" tradeoff explained in
[`docs/javascript.md`](../../docs/javascript.md), taken the other way here because this demo
already has a Node toolchain for React.

## Node/Vite constraint

Verified 2026-09-24: this machine runs Node v20.18.1. Vite 7 requires
`^20.19.0 || >=22.12.0` and refuses to run on this version, so `web/` was scaffolded with
**Vite 6** instead:

```bash
npm create vite@6 web -- --template react
cd web
npm install -D tailwindcss @tailwindcss/vite
```

If upgrading to Node 22 LTS later, Vite 7 becomes an option again — nothing else here depends on
Vite 6 specifically.

## Seeding

```bash
python demos/labeling-fastapi-react/api/seed.py
```

[`api/seed.py`](api/seed.py) creates the **same three users, same passwords, same 30 items,
assigned the same round-robin way** as `../labeling-django/`'s `seed_demo` command — see
[`../sample-data/README.md`](../sample-data/README.md) for why sharing the raw data matters, and
`api/seed.py`'s docstring for exactly how the two seed scripts are kept in sync.

**Demo credentials — local dev only, never real passwords** (identical to Demo 1):

| Username | Password | Role |
|---|---|---|
| `admin` | `demo-admin-pw` | `is_admin=True`, can call `GET /admin/labels` |
| `alice` | `demo-alice-pw` | Reviewer |
| `bob` | `demo-bob-pw` | Reviewer |

## Tests

`api/tests/test_api.py` uses FastAPI's `TestClient` against an isolated, temporary SQLite
database per test — see `api/database.py`'s `make_session_factory()` and
`api/main.py`'s `create_app(sqlite_path=...)`, the same testability idiom
`rest-apis-flask/library-crud/app.py`'s `create_app(sqlite_uri=...)` uses. The load-bearing test,
`test_reviewer_cannot_get_another_reviewers_item`, is the exact counterpart of
`../labeling-django/labeling/tests.py`'s `test_reviewer_cannot_open_another_reviewers_item` —
running the same assertion against both stacks is the actual comparison these two demos exist to
make.

## Run it

Two terminals, both from the repo root:

```bash
# Terminal 1 - the API, with .venv active
python demos/labeling-fastapi-react/api/seed.py
uvicorn main:app --reload --app-dir demos/labeling-fastapi-react/api

# Terminal 2 - the front end
cd demos/labeling-fastapi-react/web
npm install
npm run dev
```

Then open http://localhost:5173/, log in as `alice` or `bob`, and label a few tickets (mouse
click or `1`/`2`/`3` keys). Tests:

```bash
pytest demos/labeling-fastapi-react/api/tests
```

## Manual checks

1. Open http://127.0.0.1:8000/docs (FastAPI's auto-generated Swagger UI) and drive the whole
   flow from there — `POST /auth/login`, "Authorize" with the returned token, then
   `GET /items`, `GET /items/{item_id}`, `POST /items/{item_id}/label`, and `GET /admin/labels`
   as `admin`. This is the blog's "a free test form" claim.
2. Log in as `alice` in one browser tab, note an item id from her queue; log in as `bob` in
   another (or via `/docs`) and request that same id from `GET /items/{item_id}` — expect a 404,
   matching the same check in `../labeling-django/`.
3. In the React app, label a few items with the `1`/`2`/`3` keys and watch it auto-advance with
   no page reload — the interactivity payoff this stack is here to demonstrate.

## Reproducing this demo

[`PROMPT.md`](PROMPT.md) is the build prompt this demo was implemented from, kept for future
reference (e.g. to rebuild the same demo, with the same gotchas already worked out, elsewhere).
