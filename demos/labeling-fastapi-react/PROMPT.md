# Build prompt: Demo 2 — FastAPI + React labeling app

Saved for future reference — hand this to a fresh Claude Code session to rebuild this demo from
scratch (e.g. in another repo with the same conventions). See [`README.md`](README.md) for what
was actually built and how to run it.

---

Build a FastAPI + React demo at demos/labeling-fastapi-react/ (api/ + web/), the same labeling
task as demos/labeling-django/ (if that doesn't exist, see its prompt first - both demos must
read the same demos/sample-data/predictions.json by relative path so they're a fair comparison).

Before touching React: check the installed Node version (`node --version`). Vite 7 requires
Node ^20.19.0 || >=22.12.0 and will refuse to run on an older Node 20.x - if that's the case here,
scaffold with `npm create vite@6 web -- --template react` instead of unpinned `npm create vite`,
and record the exact command + why in the README.

api/ (flat layout, no src/ package - see docs/python-implementation.md):
- models.py: SQLAlchemy 2.0 typed declarative (Mapped/mapped_column) - User(username,
  hashed_password, is_admin), Item(text, model_label, model_score, assigned_to_id nullable FK),
  Label(item_id FK, reviewer_id FK, decision, corrected_label, note, created_at,
  UniqueConstraint(item_id, reviewer_id)) - same shape as the Django models, that's deliberate.
- database.py: `make_session_factory(sqlite_path=None)` returning a sessionmaker, calling
  Base.metadata.create_all() (comment: a real project would use Alembic). Module-level
  SessionLocal = make_session_factory() as the default.
- security.py: OAuth2-password + JWT pattern from FastAPI's own docs. pwdlib[argon2] for password
  hashing (not passlib - unmaintained; not fastapi-users - maintenance mode), PyJWT for
  mint/verify. A hardcoded dev-only SECRET_KEY, same spirit as Django's generated
  SECRET_KEY = 'django-insecure-...'.
- deps.py: get_db() (yield a session, close in finally), get_current_user() (decode JWT, look up
  User), require_admin(), and get_owned_item(item_id, current_user, db) - ONE shared dependency
  that 404s unless the item belongs to current_user. In the docstring/README, be explicit that
  sharing this function doesn't make the check automatic: count exactly how many routes use it.
- schemas.py: Pydantic v2 (ConfigDict(from_attributes=True)) - Token, ItemOut, ItemDetailOut
  (+ my_label), LabelIn (decision: Literal["correct","incorrect","unsure"]), LabelOut,
  AdminLabelOut.
- main.py: `create_app(sqlite_path=None)` factory + module-level `app = create_app()` (matches
  rest-apis-flask/library-crud/app.py's idiom). CORSMiddleware scoped to http://localhost:5173
  only. Routes: POST /auth/login, GET /items (list - filtered inline, CANNOT reuse
  get_owned_item since that's single-item only - this is a second, separately-written place the
  ownership rule has to be remembered), GET /items/{id} (Depends(get_owned_item)),
  POST /items/{id}/label (Depends(get_owned_item), upsert the Label), GET /admin/labels
  (Depends(require_admin) - the hand-built equivalent of Django admin, no React page for it).
- seed.py: same usernames/passwords/round-robin assignment as the Django demo's seed_demo, so the
  two demos are directly comparable.
- Dependencies needed in the repo's root requirements.in (pip-tools workflow - edit
  requirements.in, compile, sync, never hand-edit requirements.txt or bare pip install): fastapi,
  uvicorn, pyjwt, pwdlib[argon2], httpx (required by FastAPI's TestClient, not bundled),
  python-multipart (required for OAuth2PasswordRequestForm's form body, not bundled).
- tests/test_api.py + conftest.py: pytest + TestClient against an isolated tmp_path sqlite db per
  test (via create_app(sqlite_path=...)). Load-bearing test: one reviewer's token requesting
  another reviewer's item id gets 404 - the exact counterpart of the Django demo's ownership test.
  Also test login success/failure, no-token-is-401, label submit/resubmit, admin-only 403 for
  non-admins.

web/ (Vite + React, scaffolded per the Node check above):
- Add Tailwind 4 via `@tailwindcss/vite` (npm install -D tailwindcss @tailwindcss/vite), not the
  CDN browser build the Django demo uses - this project already has a Node toolchain, so use it.
- src/api/client.js: BASE = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000' (fallback so
  npm install && npm run dev works with zero setup), a request() helper, named exports (login,
  getItems, getItem, submitLabel, getAdminLabels) - same shape as react-hooks/README.md's own
  documented API-client pattern.
- src/components/LoginForm.jsx, ItemQueue.jsx, LabelPanel.jsx, src/App.jsx.
- LabelPanel.jsx: bind keys 1/2/3 to correct/incorrect/unsure (a window keydown listener, ignore
  it while an <input> has focus). App.jsx auto-advances to the next unlabeled item after each
  submit. This is the actual payoff of climbing to this stack - don't skip it as "extra scope".
- .env.example documenting VITE_API_URL.
- Persist the JWT to localStorage so a page refresh doesn't log the user out.

Write demos/labeling-fastapi-react/README.md: the auth contrast (count the lines vs. Django's
zero), the ownership table (which routes use get_owned_item vs. the separate inline filter -
3 total places, only 2 sharing code), the admin contrast (no React page, exercise via /docs
Swagger), the Node/Vite version note if it applied, seeding + credentials (identical to Demo 1),
tests, and a two-terminal run block (uvicorn + npm run dev).

Verify by actually running both processes together: seed, start the API, start Vite, log in via
curl/node with the exact fetch shape client.js uses, confirm the ownership 404, run pytest,
run npm run build and npm run lint clean.
