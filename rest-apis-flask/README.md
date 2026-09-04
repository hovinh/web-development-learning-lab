# rest-apis-flask

Notes for working through *Building REST APIs with Flask* (Kunal Relan).

Follows this repo's default convention: one subfolder per stage/chapter,
each self-contained. See the root [README.md](../README.md) for the
full list of stages across all books.

Stages so far:

- [`hello-world/`](hello-world/README.md) — smallest possible Flask
  app: one route, one plain-text response.
- [`library-crud/`](library-crud/README.md) — full CRUD REST API for
  `Author`/`Book` (one-to-many), using Flask-SQLAlchemy and Marshmallow
  together.

## What Flask actually is

Flask calls itself a "micro" framework — unlike Django, it doesn't ship
an ORM, an admin site, or a forms library out of the box. What it *does*
provide is thin: routing, request/response handling, and templating. It
does that by combining two separate libraries, each solving one problem:

- **[Werkzeug](https://werkzeug.palletsprojects.com/)** — the WSGI
  toolkit. This is the part that talks HTTP: it parses incoming
  requests, builds outgoing responses, matches URLs to view functions
  (routing), and provides the dev server plus an interactive debugger.
  In other words, Werkzeug is the web-server-facing plumbing — Flask's
  `Request`/`Response` objects and its `@app.route()` decorator are
  thin wrappers around Werkzeug classes.
- **[Jinja2](https://jinja.palletsprojects.com/)** — the templating
  engine. This is the part that turns a template file plus a context
  dict into rendered output (usually HTML), via `{{ variable }}`
  expressions and `{% tag %}` logic (`if`/`for`/`extends`/`block`,
  familiar from Django's own template language, which Jinja2's syntax
  was modeled after). Flask's `render_template()` is just Jinja2 under
  the hood.

For a REST API specifically, Jinja2 mostly stays idle — JSON responses
(`jsonify()`) don't need HTML templates — so most of what this book's
stages will lean on is Werkzeug: routing, request parsing, and status
codes/headers on the response.

## Persistence and serialization: Flask-SQLAlchemy and Marshmallow

Flask being "micro" means an ORM and a serialization layer aren't
included — this book adds both as separate libraries, each solving a
different half of the "database row in, JSON out" problem:

- **[Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)**
  — wires SQLAlchemy's ORM into a Flask app: a `db = SQLAlchemy(app)`
  extension object that manages the database connection/session
  lifecycle per-request, plus `db.Model` as the declarative base class
  for model classes (`db.Column`, `db.relationship`, etc). This is the
  same underlying SQLAlchemy already used standalone in
  `dataviz-python-js/data-read-write` and `dataviz-python-js/data-serve`
  — Flask-SQLAlchemy just removes the boilerplate of managing engine/
  session setup and teardown by hand inside a Flask app.
- **[Marshmallow](https://marshmallow.readthedocs.io/)** — converts
  between Python objects (e.g. a SQLAlchemy model instance) and plain
  JSON-serializable data, in both directions: a `Schema` class's
  `dump()` turns a model instance into a dict ready for `jsonify()`,
  and `load()` turns incoming request JSON into validated Python data
  (raising on missing/malformed fields) before it touches a model.
  Where Flask-SQLAlchemy is the DB-facing half, Marshmallow is the
  API-facing half — it's what keeps validation and response shaping
  out of the view functions themselves. (`flask-marshmallow` is the
  thin Flask integration layer some stages may use on top of it, e.g.
  for hyperlinked fields — added if/when a stage actually needs it.)

Together, a typical request in a later stage flows: JSON in → Marshmallow
`load()` validates it → Flask-SQLAlchemy `db.Model` persists it →
Marshmallow `dump()` serializes the result → `jsonify()` sends it back.
