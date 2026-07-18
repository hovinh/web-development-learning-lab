# data-serve

Serves [`data-process`](../data-process/README.md)'s cleaned dataset as
a REST API via Flask - both the structured data (name, types, stats, ...)
and the unstructured data (each Pokemon's artwork image), behind two
interchangeable backends.

## The idea

One Flask app, one set of routes, two backends that can serve them:

- **`file` backend** (default) - reads `data-process/pokedex.json` into
  memory once at startup and serves artwork by reading straight from
  `data-process/images/` per request. No database at all.
- **`sqlite` backend** - a real database (`data-serve/pokedex.db`,
  built by `load_sqlite.py`), queried through
  [Flask-SQLAlchemy](https://flask-sqlalchemy.readthedocs.io/). Each
  Pokemon's artwork is stored as a BLOB column in the same database -
  see "Notes on storing images in SQLite vs. production options" below
  for why that's a fine way to *learn* the tradeoff and not the
  recommended way to actually ship this.

Both backends are wired into the exact same routes in `app.py`, which
only ever calls a `repository` object's `get_all()`/`get_one()`/
`get_artwork_response()`/`count()` - never data-process's files or the
database directly. That's what makes the two backends produce
byte-identical JSON and byte-identical images for the same request (see
"Testing" below for how that's actually verified, not just claimed).

## Endpoints

| Method & path | Returns | Notes |
|---|---|---|
| `GET /api/meta` | `{"backend": "file" \| "sqlite", "count": <int>}` | Which backend is live and how much data it has - mostly for the smoke-test scripts below. |
| `GET /api/pokemon` | A JSON array of structured Pokemon records | Query params: `type` (case-insensitive, e.g. `?type=fire`), `generation` (`?generation=1`), `limit`/`offset` (default `50`/`0`), sorted by national number. |
| `GET /api/pokemon/<name>` | One structured Pokemon record, or `404` | `<name>` is the lowercase slug, e.g. `pikachu`. |
| `GET /api/pokemon/<name>/artwork` | Raw JPEG bytes (`Content-Type: image/jpeg`), or `404` | The unstructured half of this stage - not JSON. |

A structured record's shape (identical from both backends):

```json
{
  "national_number": 25,
  "name": "pikachu",
  "display_name": "Pikachu",
  "generation": 1,
  "species": "Mouse Pokémon",
  "types": ["Electric"],
  "abilities": ["Static", "Lightning Rod"],
  "hidden_ability": "Lightning Rod",
  "height_m": 0.4,
  "weight_kg": 6.0,
  "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
  "artwork_url": "/api/pokemon/pikachu/artwork"
}
```

`artwork_url` points back at this same API rather than exposing
data-process's local `images/bulbasaur.jpg`-style relative path - a
filesystem path on this server means nothing to a remote client, an API
URL does.

## Choosing a backend

| | `file` | `sqlite` |
|---|---|---|
| Setup | none - just run `app.py` | run `load_sqlite.py` once first |
| Filtering (`?type=`/`?generation=`) | a linear Python scan over every record, every request | a real `WHERE`/`OR` clause - see `sqlite_repository.py` |
| Where artwork lives | read from disk per request | stored as a BLOB column, read from the database per request |
| Reach for it when... | the dataset comfortably fits in memory and query needs stay simple (this stage's ~700 Pokemon, easily) | you want to see how filtering/pagination push down into real SQL, or you're specifically comparing against the file backend |

Neither backend is "the right one" here - the whole point of this stage
is having both behind the same API to compare, the same spirit as
[`data-read-write`](../data-read-write/README.md) building the same
pipeline three ways (SQLAlchemy/`dataset`/MongoDB) for comparison rather
than picking one.

## Notes on the schema (`models.py`)

- `types` is stored as two flat columns, `type_1`/`type_2` (nullable) -
  this mirrors `data-read-write/models.py`'s `Pokemon.type_1`/`type_2`
  columns for the identical reason: every Pokemon in this dataset has 1
  or 2 types, never more, and a fixed, small shape is exactly what flat
  columns are for.
- `abilities` is stored as a single `JSON` column instead, since its
  length genuinely varies (1-3 in this dataset) - SQLite has no native
  array column type, and a fixed number of ability columns wouldn't fit
  as cleanly as it does for types. SQLAlchemy's `JSON` type stores it as
  JSON text under the hood but hands back a plain Python list
  transparently - `pokemon.abilities` never looks any different from
  the file backend's list.
- That split - flat columns for a fixed-size field, a JSON column for a
  variable-size one - is a small, concrete version of the same tension
  that motivated trying MongoDB for `data-read-write`'s nested `stats`
  dict: flat relational columns fit a uniform shape; reach for
  document-shaped storage once it doesn't.

## Notes on storing images in SQLite vs. production options

`load_sqlite.py` reads every artwork JPEG into an `artwork_blob` column
so the sqlite backend can demonstrate that a relational database *can*
hold unstructured binary data right next to structured columns - useful
to see once, not the recommended way to actually run this:

- **It bloats the database file.** `data-serve/pokedex.db` is now
  several megabytes of JPEG bytes mixed into the same file as
  `national_number`/`type_1`/etc. - every query, backup, and replication
  of that database now has to move image bytes around even when nobody
  asked for an image.
- **No CDN-friendly access.** A file on disk (or in object storage) can
  be served directly by a static file server or CDN with caching,
  range requests, etc. for free - `send_file()` in `file_repository.py`
  already gets some of this from Flask; a BLOB column gets none of it
  without extra work.
- **What's actually better for production**: this is exactly the
  situation [MongoDB](https://www.mongodb.com/) (or a document store in
  general) is a stronger fit for than a relational database - either
  [GridFS](https://www.mongodb.com/docs/manual/core/gridfs/) (MongoDB's
  built-in mechanism for storing files larger than its 16MB document
  limit, chunked across a collection) for the images themselves, or more
  commonly in real production systems: images in an object store (S3
  and similar) with only a URL/key stored in the database - structured
  data stays structured, unstructured data goes wherever unstructured
  data is actually served well from. `data-read-write` already
  demonstrates MongoDB for this repo's structured data too (its nested
  `stats` dict); this stage deliberately doesn't reach for MongoDB
  itself (per the scope of this exercise) so the SQLite BLOB approach
  stays the point of comparison - see that stage's `mongo_store.py` for
  what MongoDB actually looks like here.

## CORS

Every `/api/*` route is wrapped in [Flask-Cors](https://flask-cors.readthedocs.io/)
(`CORS(app, resources={r"/api/*": {"origins": "*"}})` in `app.py`), so a
browser page served from a *different* origin - not this server - is
allowed to call this API with `fetch()`/`d3.json()`. That's needed
because [`d3-interactive-web`](../d3-interactive-web/README.md) is
served by `http-server` on its own port (typically `localhost:8080`)
while this API runs on `localhost:5000`: without CORS headers, the
browser blocks the response before that page's JavaScript ever sees
it, even though both are `localhost`. `origins: "*"` is fine for a
local learning server with no auth or write endpoints to protect - and
stays fine in the public deployment (see `../deploy/README.md`) since
that's also a read-only API over public data; a deployment with
anything sensitive behind it would scope this to the actual frontend's
origin instead of allowing any.

## Notes on flask-restless (evaluated, not used)

[Flask-Restless](https://flask-restless.readthedocs.io/) auto-generates
REST endpoints straight from SQLAlchemy models, which sounded like a
good fit for the `sqlite` backend - it was tried before hand-writing
`app.py`'s routes. It doesn't work on this repo's stack:

```
ImportError: cannot import name 'url_quote_plus' from 'werkzeug.urls'
```

Flask-Restless's last release was **0.17.0 in February 2015**, targeting
Python 2.6/2.7/3.3/3.4 - it imports a Werkzeug function
(`url_quote_plus`) that was removed years ago, and fails at `import
flask_restless` before any of its own code runs, under the Flask 3.x/
Werkzeug 3.x this repo already uses elsewhere. Making it work would mean
pinning a decade-old Flask/Werkzeug just for this one stage, which isn't
a reasonable trade for a learning repo (or a real project). Hand-written
routes calling a plain repository object turned out to be barely more
code than configuring Flask-Restless would have been, and it's more
instructive besides - explicit HTTP methods/status codes/query-param
handling, rather than a library's generated behavior to reverse-engineer.

`Flask-SQLAlchemy` (unrelated project, despite the similar name) is
actively maintained and is what the `sqlite` backend actually uses for
its `db.Model`/session integration.

## Files

- `config.py` - shared paths (`data-process`'s JSON/images, this stage's
  own `pokedex.db`).
- `models.py` - the `sqlite` backend's `Pokemon` model + `to_dict()`.
- `file_repository.py` - the `file` backend.
- `sqlite_repository.py` - the `sqlite` backend.
- `app.py` - `create_app()` (Flask app factory, picks a backend) and
  every route.
- `load_sqlite.py` - builds `data-serve/pokedex.db` from
  `data-process`'s output; run once before using the `sqlite` backend.
- `tests/test_app.py` - pytest, in-process (`Flask.test_client()`, no
  real server/port) - every test is parametrized over both backends.
- `smoke_test.py`, `smoke_test.js` - manual scripts that hit a *real*,
  running server over actual HTTP; see "Manual smoke testing" below.
- `conftest.py` - empty; lets `tests/` import this stage's modules
  without a package (same as the other data stages).
- `pokedex.db` - generated by `load_sqlite.py`; not committed (see root
  `.gitignore`), fully reproducible from `data-process`'s output.

## Testing

`tests/test_app.py` uses Flask's `test_client()` - no real server or
port involved - with a `client` fixture parametrized over both backends,
so every test runs twice (once per backend) against hand-built synthetic
data. That parametrization is the actual point: testing only one backend
would miss the one thing this stage is really about, whether they agree.

```bash
pytest data-serve/tests
```

## Manual smoke testing

`smoke_test.py`/`smoke_test.js` are different from `tests/test_app.py`
on purpose: they hit a server you've actually started, over a real
socket, in whichever language - the end-to-end check that the thing
works as an HTTP API, not just that the Flask routing logic is correct
in-process. `smoke_test.js` uses Node's built-in `http` module (not
`fetch`, which is only global since Node 18) so it runs with no
dependency and no minimum Node version bump.

```bash
# In one terminal:
python data-serve/app.py
# (or: DATA_SERVE_BACKEND=sqlite python data-serve/app.py, after load_sqlite.py)

# In another terminal, either or both:
python data-serve/smoke_test.py
node data-serve/smoke_test.js
```

Both exit non-zero if any check fails, and print a clear message (rather
than a raw connection-error traceback) if no server is reachable at all.

## Running

Add the new dependencies first, if you haven't already synced the venv:

```bash
.venv/Scripts/python.exe -m piptools sync requirements.txt
```

Then, from the repo root with `.venv` active:

```bash
# file backend - no setup needed
python data-serve/app.py

# sqlite backend - build the database first
python data-serve/load_sqlite.py
DATA_SERVE_BACKEND=sqlite python data-serve/app.py
```

Requires `data-process/pokedex.json` and `data-process/images/` - both
are committed to this repo (see that stage's README's "Files" section),
so a fresh clone already has them and the `file` backend needs nothing
else to run. The `sqlite` backend only reads them once, when
`load_sqlite.py` builds `pokedex.db`; after that the backend runs off
`pokedex.db` alone. If you ever need to regenerate `pokedex.json`/
`images/` from scratch, run `data-process/process_pokedex.py` (see that
stage's README).

The server defaults to `http://localhost:5000` (Flask's default); set
`PORT` to change it.

## Deployment

`app.py` also defines `app` at module level (not just inside
`if __name__ == "__main__":`), so a production WSGI server can import
it as `app:app` instead of using Flask's own single-threaded dev
server. That's what [`../deploy/render.yaml`](../deploy/render.yaml)
does, running `gunicorn app:app` on Render's free tier - see
[`../deploy/README.md`](../deploy/README.md) for the full setup, why
the `sqlite` backend is the one deployed, and free-tier tradeoffs like
cold starts.
