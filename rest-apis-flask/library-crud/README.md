# library-crud

A small library API: full CRUD for `Author` and `Book`, with a
one-to-many relationship between them (an author has many books). First
stage to actually use Flask-SQLAlchemy and Marshmallow together — see
the [book's README](../README.md#persistence-and-serialization-flask-sqlalchemy-and-marshmallow)
for how the two divide the work. Also the first stage with generated API
docs — see "API docs (Swagger UI)" below, and the book README's
[API documentation](../README.md#api-documentation-the-openapi-spec-and-swagger-ui)
section for what `flask-smorest` is doing.

## What's here

- [`models.py`](models.py) — `Author`/`Book` SQLAlchemy models, wired to
  a SQLite database via Flask-SQLAlchemy. `Author.books` is a
  relationship with `cascade="all, delete-orphan"`, so deleting an
  author deletes their books too.
- [`schemas.py`](schemas.py) — Marshmallow schemas that validate
  incoming JSON (`load()`) and shape outgoing JSON (`dump()`). Each
  side nests a *summary* of the other (`BookSummarySchema` inside
  `AuthorSchema`, `AuthorSummarySchema` inside `BookSchema`) rather than
  the full schema, which would otherwise nest into itself forever.
  These same schema classes also drive the generated OpenAPI spec (see
  `resources/`) — one schema definition, not a separate copy for docs.
- [`resources/authors.py`](resources/authors.py) and
  [`resources/books.py`](resources/books.py) — the actual routes, as
  `flask-smorest` `Blueprint`s of `MethodView` resources rather than
  plain `@app.route` functions. `@blp.arguments(Schema)` validates the
  request body against a schema before the view body runs (a mismatch
  returns `422`, not `400` — see "Validation errors" below);
  `@blp.response(status, Schema)` serializes whatever a view returns and
  records that shape in the OpenAPI spec. `resources/books.py` still has
  one explicit check a schema can't express — that `author_id` actually
  points at an existing author.
- [`app.py`](app.py) — the Flask app: `create_app()` builds it, wires up
  the database, registers those two Blueprints with a `flask_smorest.Api`
  (which is what turns them into the OpenAPI spec + Swagger UI), and
  defines the bare `/` index. Run directly with `python app.py`.
- [`config.py`](config.py) — the SQLite database path/URI.
- [`seed.py`](seed.py) — populates `library.db` with a handful of
  authors/books, so the API has something in it right away instead of
  starting empty. Run it once before starting the server (see "Seeding
  data" below).
- [`tests/test_app.py`](tests/test_app.py) — CRUD tests via Flask's
  `test_client()`, each against its own temporary SQLite file. Uses
  `pytest`, this repo's usual test tool.
- [`tests/test_app_unittest.py`](tests/test_app_unittest.py) — a slice
  of that same coverage, rewritten as `unittest.TestCase` classes and
  run with `nose2` — see "Testing" below for why this stage has two
  test files/tools instead of just `pytest`.

## Endpoints

| Method | Path                  | Body                                          |
|--------|-----------------------|------------------------------------------------|
| GET    | `/api/authors`        | —                                                |
| GET    | `/api/authors/<id>`   | —                                                |
| POST   | `/api/authors`        | `{"name": "..."}`                                |
| PUT    | `/api/authors/<id>`   | `{"name": "..."}`                                |
| DELETE | `/api/authors/<id>`   | — (also deletes their books)                     |
| GET    | `/api/books`          | —                                                |
| GET    | `/api/books/<id>`     | —                                                |
| POST   | `/api/books`          | `{"title": "...", "published_year": 1974, "author_id": 1}` |
| PUT    | `/api/books/<id>`     | same shape as POST                               |
| DELETE | `/api/books/<id>`     | —                                                |

## Validation errors

A malformed/missing field in a POST or PUT body never reaches the
database — `flask-smorest`'s `@blp.arguments(Schema)` rejects it first
(via the same Marshmallow schemas as `schemas.py`) and the route returns
`422 Unprocessable Entity`, with Marshmallow's field-by-field error
messages nested under `errors.json`:

```json
{
  "code": 422,
  "status": "Unprocessable Entity",
  "errors": {"json": {"name": ["Missing data for required field."]}}
}
```

Creating a book with an `author_id` that doesn't exist is a different
kind of failure — the body *is* shaped correctly, `author_id` is just an
int that doesn't reference a real row — so it's checked explicitly in
`resources/books.py` instead of by the schema, and returns a plain `400`
(SQLite's foreign-key enforcement isn't reliably on by default, so this
can't be left to the database either).

## API docs (Swagger UI)

With the server running (see "Running it" below):

- **`/docs`** — interactive Swagger UI. Every endpoint above, browsable,
  each with a "Try it out" button that sends a real request against
  whatever's currently in `library.db` and shows the actual response —
  a working alternative to the `curl` examples below.
- **`/openapi.json`** — the raw generated OpenAPI document Swagger UI
  renders, if something else needs to consume the spec directly (e.g.
  generating a client SDK).

Both are generated from `resources/authors.py`/`resources/books.py`'s
route decorators and `schemas.py`'s schemas — there's no separate docs
file to keep in sync by hand.

## Seeding data

`app.py` alone starts with an empty database (`create_app()` only calls
`db.create_all()`, which makes the tables but adds no rows). To have a
few authors/books already there:

```bash
.venv\Scripts\Activate.ps1   # PowerShell
python rest-apis-flask/library-crud/seed.py
```

This **drops and recreates every table**, so it's meant to run once
before starting the server, not while it's running against data you
want to keep — same "build the data, then serve it" split as
`dataviz-python-js/data-serve/load_sqlite.py`. It seeds 3 authors
(Ursula K. Le Guin, Octavia E. Butler, Ted Chiang) and 5 books between
them (see `SEED_AUTHORS` in `seed.py` to change what's seeded).

## Running it

From the repo root, with the shared venv active:

```bash
.venv\Scripts\Activate.ps1   # PowerShell
python rest-apis-flask/library-crud/app.py
```

The first run creates `library.db` in this folder if it doesn't already
exist (gitignored, reproducible by re-running the app — `create_app()`
calls `db.create_all()` on startup; run `seed.py` first if you want it
pre-populated). Once it's running, open http://127.0.0.1:5000/docs for
Swagger UI, or hit the API directly:

```bash
curl -X POST http://127.0.0.1:5000/api/authors -H "Content-Type: application/json" -d "{\"name\": \"Ursula K. Le Guin\"}"
curl -X POST http://127.0.0.1:5000/api/books -H "Content-Type: application/json" -d "{\"title\": \"The Dispossessed\", \"published_year\": 1974, \"author_id\": 1}"
curl http://127.0.0.1:5000/api/authors/1
```

## Testing

`pytest`, from the repo root (this repo's usual test tool — see
[docs/python-implementation.md](../../docs/python-implementation.md#testing)):

```bash
pytest rest-apis-flask/library-crud/tests
```

This book also has a chapter on unit testing with **nose** — but classic
`nose` is unmaintained (last released 2015) and no longer even imports on
Python 3.10+ (it uses `collections.Callable`, removed that version), so
this stage uses **[nose2](https://docs.nose2.io/)** instead, its
maintained successor and the closest thing still runnable today.
`tests/test_app_unittest.py` covers the same core routes rewritten in
the classic `unittest.TestCase` style (`setUp`/`tearDown`,
`self.assert*`) that both `nose` and `nose2` build on top of, run from
*inside* this stage's directory rather than the repo root:

```bash
cd rest-apis-flask/library-crud
python -m nose2 -v
```

That `cd` matters here in a way it doesn't for pytest: pytest finds
`app.py`/`models.py` etc. via this stage's `conftest.py`, which adds the
stage directory to `sys.path` no matter where pytest itself is invoked
from. `nose2` has no such hook — it relies on its own test-discovery
behavior adding its *current working directory* to `sys.path`, so it
only resolves `from app import create_app` when run with this directory
as `cwd`. `nose2` doesn't pick up `test_app.py` in the same run because
it only collects `unittest.TestCase` subclasses, not the plain
pytest-fixture-style functions that file uses.
