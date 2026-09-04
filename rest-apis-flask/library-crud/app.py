"""The Flask app: CRUD REST endpoints for Authors and Books.

Routing lives in resources/authors.py and resources/books.py as
flask-smorest Blueprints of MethodView resources, not directly in this
file - see those modules' docstrings for what changed from the original
plain-Flask routes. This file's job is just to build the app, wire up
the database, and register those Blueprints with a flask-smorest `Api`,
which is what turns them into a generated OpenAPI spec + Swagger UI (see
rest-apis-flask/README.md's "API documentation" section) on top of the
same request/response behavior as before.

## Endpoints

Authors:
- `GET    /api/authors`           - list all authors (each with a nested
  `books` summary - see schemas.py).
- `GET    /api/authors/<id>`      - one author.
- `POST   /api/authors`           - create an author. Body: `{"name": ...}`.
- `PUT    /api/authors/<id>`      - replace an author's fields.
- `DELETE /api/authors/<id>`      - delete an author and (cascading) all
  of their books - see models.py's Author.books relationship.

Books:
- `GET    /api/books`             - list all books (each with a nested
  `author` summary).
- `GET    /api/books/<id>`        - one book.
- `POST   /api/books`             - create a book. Body:
  `{"title": ..., "published_year": ..., "author_id": ...}`.
- `PUT    /api/books/<id>`        - replace a book's fields.
- `DELETE /api/books/<id>`        - delete a book.

Every write route (POST/PUT) runs the request body through a Marshmallow
schema before it reaches the database - flask-smorest's `@blp.arguments`
decorator does this now (see resources/), returning 422 with Marshmallow's
own field-by-field error messages on a malformed or missing field.

## API docs

With the server running: interactive Swagger UI is at `/docs`, the raw
generated OpenAPI document at `/openapi.json`.
"""

from __future__ import annotations

from flask import Flask, jsonify
from flask_smorest import Api

from config import SQLITE_DATABASE_URI
from models import db
from resources.authors import blp as AuthorBlueprint
from resources.books import blp as BookBlueprint


def create_app(sqlite_uri: str | None = None) -> Flask:
    """Build the Flask app.

    `sqlite_uri` lets tests/test_app.py point this same app at an
    isolated, temporary database instead of library.db - same pattern as
    dataviz-python-js/data-serve/app.py's create_app().
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = sqlite_uri or SQLITE_DATABASE_URI
    db.init_app(app)

    with app.app_context():
        # Fine for a learning stage with one small SQLite file - a real
        # project would use migrations (e.g. Flask-Migrate/Alembic)
        # instead of create_all() so schema changes don't require
        # dropping data.
        db.create_all()

    # flask-smorest config: what it needs to generate the OpenAPI
    # document and serve Swagger UI on top of it. OPENAPI_SWAGGER_UI_URL
    # points at a CDN build of the swagger-ui-dist JS/CSS assets - this
    # app doesn't vendor or serve them itself.
    app.config["API_TITLE"] = "Library CRUD API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    api = Api(app)
    api.register_blueprint(AuthorBlueprint)
    api.register_blueprint(BookBlueprint)

    @app.get("/")
    def index():
        # There's no HTML page at the bare root - this stage is
        # JSON-only, no Jinja2 templates involved (see
        # rest-apis-flask/README.md's "What Flask actually is"). This
        # route just points a browser or curl hitting "/" at the actual
        # API and its docs instead of a bare 404.
        return jsonify(
            {
                "authors": "/api/authors",
                "books": "/api/books",
                "docs": "/docs",
                "openapi_spec": "/openapi.json",
            }
        )

    return app


# Module-level, not just inside __main__ - see
# dataviz-python-js/data-serve/app.py for why: a production WSGI server
# would import this module and look for `app` directly.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
