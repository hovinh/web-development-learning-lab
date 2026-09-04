"""The library's schema: an Author has many Books (one-to-many).

`db = SQLAlchemy()` is created unbound (no app yet) and wired to a real
Flask app later via `db.init_app(app)` in app.py's create_app() - same
Flask-SQLAlchemy pattern as dataviz-python-js/data-serve/models.py, and
what lets tests/test_app.py point the same model classes at a temporary,
isolated database file instead of library.db.
"""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # back_populates keeps both sides of the relationship in sync (an
    # Author knows its Books, a Book knows its Author) without either
    # side going stale when the other changes in the same session.
    # cascade="all, delete-orphan" means deleting an author also deletes
    # their books - the simplest policy for a learning stage; a real
    # library API might instead forbid deleting an author who still has
    # books, or reassign them.
    books = db.relationship(
        "Book", back_populates="author", cascade="all, delete-orphan"
    )


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    published_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    author = db.relationship("Author", back_populates="books")
