"""The Flask app: CRUD REST endpoints for Authors and Books.

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
schema's `load()` first - a malformed or missing field never reaches the
database, and comes back as a 400 with Marshmallow's own field-by-field
error messages rather than a raw database exception.
"""

from __future__ import annotations

from flask import Flask, abort, jsonify, request
from marshmallow import ValidationError

from config import SQLITE_DATABASE_URI
from models import Author, Book, db
from schemas import AuthorSchema, BookSchema

# One schema instance per shape is enough - Marshmallow schemas are
# stateless and safe to reuse across requests, unlike a per-request model
# instance.
author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)
book_schema = BookSchema()
books_schema = BookSchema(many=True)


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

    @app.get("/")
    def index():
        # There's no page at the bare root - this stage is JSON-only, no
        # Jinja2 templates involved (see rest-apis-flask/README.md's
        # "What Flask actually is"). This route just points a browser or
        # curl hitting "/" at the actual API instead of a bare 404.
        return jsonify(
            {
                "authors": "/api/authors",
                "books": "/api/books",
            }
        )

    # ---- Authors ----

    @app.get("/api/authors")
    def list_authors():
        authors = Author.query.order_by(Author.id).all()
        return jsonify(authors_schema.dump(authors))

    @app.get("/api/authors/<int:author_id>")
    def get_author(author_id: int):
        author = db.session.get(Author, author_id)
        if author is None:
            abort(404, description=f"No author with id {author_id}")
        return jsonify(author_schema.dump(author))

    @app.post("/api/authors")
    def create_author():
        try:
            data = author_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return jsonify(err.messages), 400

        author = Author(name=data["name"])
        db.session.add(author)
        db.session.commit()
        return jsonify(author_schema.dump(author)), 201

    @app.put("/api/authors/<int:author_id>")
    def update_author(author_id: int):
        author = db.session.get(Author, author_id)
        if author is None:
            abort(404, description=f"No author with id {author_id}")

        try:
            data = author_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return jsonify(err.messages), 400

        author.name = data["name"]
        db.session.commit()
        return jsonify(author_schema.dump(author))

    @app.delete("/api/authors/<int:author_id>")
    def delete_author(author_id: int):
        author = db.session.get(Author, author_id)
        if author is None:
            abort(404, description=f"No author with id {author_id}")

        db.session.delete(author)  # cascades to their books, see models.py
        db.session.commit()
        return "", 204

    # ---- Books ----

    @app.get("/api/books")
    def list_books():
        books = Book.query.order_by(Book.id).all()
        return jsonify(books_schema.dump(books))

    @app.get("/api/books/<int:book_id>")
    def get_book(book_id: int):
        book = db.session.get(Book, book_id)
        if book is None:
            abort(404, description=f"No book with id {book_id}")
        return jsonify(book_schema.dump(book))

    @app.post("/api/books")
    def create_book():
        try:
            data = book_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return jsonify(err.messages), 400

        if db.session.get(Author, data["author_id"]) is None:
            abort(400, description=f"No author with id {data['author_id']}")

        book = Book(
            title=data["title"],
            published_year=data["published_year"],
            author_id=data["author_id"],
        )
        db.session.add(book)
        db.session.commit()
        return jsonify(book_schema.dump(book)), 201

    @app.put("/api/books/<int:book_id>")
    def update_book(book_id: int):
        book = db.session.get(Book, book_id)
        if book is None:
            abort(404, description=f"No book with id {book_id}")

        try:
            data = book_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return jsonify(err.messages), 400

        if db.session.get(Author, data["author_id"]) is None:
            abort(400, description=f"No author with id {data['author_id']}")

        book.title = data["title"]
        book.published_year = data["published_year"]
        book.author_id = data["author_id"]
        db.session.commit()
        return jsonify(book_schema.dump(book))

    @app.delete("/api/books/<int:book_id>")
    def delete_book(book_id: int):
        book = db.session.get(Book, book_id)
        if book is None:
            abort(404, description=f"No book with id {book_id}")

        db.session.delete(book)
        db.session.commit()
        return "", 204

    return app


# Module-level, not just inside __main__ - see
# dataviz-python-js/data-serve/app.py for why: a production WSGI server
# would import this module and look for `app` directly.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
