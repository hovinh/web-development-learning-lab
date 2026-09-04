# library-crud

A small library API: full CRUD for `Author` and `Book`, with a
one-to-many relationship between them (an author has many books). First
stage to actually use Flask-SQLAlchemy and Marshmallow together — see
the [book's README](../README.md#persistence-and-serialization-flask-sqlalchemy-and-marshmallow)
for how the two divide the work.

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
- [`app.py`](app.py) — the Flask app: `create_app()` builds it, wires up
  the database, and defines every route. Run directly with
  `python app.py`.
- [`config.py`](config.py) — the SQLite database path/URI.
- [`seed.py`](seed.py) — populates `library.db` with a handful of
  authors/books, so the API has something in it right away instead of
  starting empty. Run it once before starting the server (see "Seeding
  data" below).
- [`tests/test_app.py`](tests/test_app.py) — CRUD tests via Flask's
  `test_client()`, each against its own temporary SQLite file.

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

A malformed/missing field in a POST or PUT body never reaches the
database — Marshmallow's `load()` rejects it first and the route
returns `400` with Marshmallow's own field-by-field error messages.
Creating a book with an `author_id` that doesn't exist also returns
`400` (checked explicitly in `app.py`, since SQLite's foreign-key
enforcement isn't reliably on by default).

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
pre-populated). Example requests once it's running:

```bash
curl -X POST http://127.0.0.1:5000/api/authors -H "Content-Type: application/json" -d "{\"name\": \"Ursula K. Le Guin\"}"
curl -X POST http://127.0.0.1:5000/api/books -H "Content-Type: application/json" -d "{\"title\": \"The Dispossessed\", \"published_year\": 1974, \"author_id\": 1}"
curl http://127.0.0.1:5000/api/authors/1
```

## Tests

```bash
pytest rest-apis-flask/library-crud/tests
```
