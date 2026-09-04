"""Populate library.db with a handful of authors and books.

Run this once before starting the server, if you want data to already
be there instead of an empty database - see README.md's "Seeding data"
section. "Build the data" and "serve the data" as separate, explicit
steps matches dataviz-python-js/data-serve/load_sqlite.py.

Drops and recreates every table on each run, same reasoning as that
script: this is fixed demo data fully reproducible from this file, not
something meant to persist or migrate across runs.
"""

from __future__ import annotations

from app import create_app
from models import Author, Book, db

# (author name, [(book title, published year), ...])
SEED_AUTHORS = [
    (
        "Ursula K. Le Guin",
        [
            ("The Left Hand of Darkness", 1969),
            ("The Dispossessed", 1974),
        ],
    ),
    (
        "Octavia E. Butler",
        [
            ("Kindred", 1979),
            ("Parable of the Sower", 1993),
        ],
    ),
    (
        "Ted Chiang",
        [
            ("Stories of Your Life and Others", 2002),
        ],
    ),
]


def seed() -> None:
    app = create_app()

    with app.app_context():
        db.drop_all()
        db.create_all()

        book_count = 0
        for author_name, books in SEED_AUTHORS:
            author = Author(name=author_name)
            for title, published_year in books:
                author.books.append(Book(title=title, published_year=published_year))
                book_count += 1
            db.session.add(author)

        db.session.commit()

    print(
        f"Seeded {len(SEED_AUTHORS)} authors and {book_count} books into "
        "library-crud/library.db"
    )


if __name__ == "__main__":
    seed()
