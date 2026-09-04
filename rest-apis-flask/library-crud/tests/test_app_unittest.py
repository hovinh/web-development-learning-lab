"""The same CRUD API, tested with unittest.TestCase and run by nose2.

tests/test_app.py already covers this with pytest, the repo's usual test
tool (see docs/python-implementation.md's "Testing" section). This file
exists alongside it for this book's chapter on unit testing with nose -
nose2 is what's actually used (see README.md's "Testing" section for
why: classic `nose` doesn't run on Python 3.10+).

Structurally, this is the classic unittest style nose/nose2 build on top
of: a TestCase subclass, `setUp`/`tearDown` instead of a pytest fixture,
and `self.assert*` methods instead of bare `assert`. It doesn't repeat
every case from test_app.py - just enough of each route to demonstrate
the pattern (see that file for the full matrix, e.g. every validation
edge case).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import create_app
from models import db


class LibraryApiTestCase(unittest.TestCase):
    """Base case: a fresh app + isolated temp SQLite file per test.

    unittest.TestCase's setUp()/tearDown() run before/after every test
    method on the class - the closest unittest equivalent to pytest's
    per-test `client` fixture in test_app.py.
    """

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self._tmpdir.name) / "test.db"
        self.app = create_app(sqlite_uri=f"sqlite:///{db_path}")
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        # SQLAlchemy keeps its SQLite connection open (pooled) even
        # between requests, which on Windows keeps the underlying file
        # handle locked - dispose() closes it so the temp dir below can
        # actually be removed. Not needed on Linux/macOS, but harmless
        # there either way.
        with self.app.app_context():
            db.engine.dispose()
        self._tmpdir.cleanup()


class AuthorTests(LibraryApiTestCase):
    def test_create_and_get_author(self) -> None:
        response = self.client.post("/api/authors", json={"name": "Ursula K. Le Guin"})
        self.assertEqual(response.status_code, 201)
        author = response.get_json()
        self.assertEqual(author["name"], "Ursula K. Le Guin")
        self.assertEqual(author["books"], [])

        response = self.client.get(f"/api/authors/{author['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Ursula K. Le Guin")

    def test_create_author_missing_name_is_422(self) -> None:
        # flask-smorest validates the body against AuthorSchema before
        # the view runs - see resources/authors.py - so this never
        # reaches the database.
        response = self.client.post("/api/authors", json={})
        self.assertEqual(response.status_code, 422)
        self.assertIn("name", response.get_json()["errors"]["json"])

    def test_update_author(self) -> None:
        created = self.client.post("/api/authors", json={"name": "Typo Namee"}).get_json()

        response = self.client.put(
            f"/api/authors/{created['id']}", json={"name": "Correct Name"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Correct Name")

    def test_delete_author_cascades_to_their_books(self) -> None:
        author = self.client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()
        book = self.client.post(
            "/api/books",
            json={
                "title": "The Left Hand of Darkness",
                "published_year": 1969,
                "author_id": author["id"],
            },
        ).get_json()

        response = self.client.delete(f"/api/authors/{author['id']}")
        self.assertEqual(response.status_code, 204)

        # The cascade in models.py's Author.books relationship should
        # have removed the book too, not just orphaned it.
        self.assertEqual(self.client.get(f"/api/books/{book['id']}").status_code, 404)

    def test_get_unknown_author_is_404(self) -> None:
        self.assertEqual(self.client.get("/api/authors/999").status_code, 404)


class BookTests(LibraryApiTestCase):
    def test_create_and_get_book(self) -> None:
        author = self.client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()

        response = self.client.post(
            "/api/books",
            json={
                "title": "The Dispossessed",
                "published_year": 1974,
                "author_id": author["id"],
            },
        )
        self.assertEqual(response.status_code, 201)
        book = response.get_json()
        self.assertEqual(book["title"], "The Dispossessed")
        self.assertEqual(book["author"]["name"], "Ursula K. Le Guin")

    def test_create_book_with_unknown_author_is_400(self) -> None:
        response = self.client.post(
            "/api/books",
            json={"title": "Orphan Book", "published_year": 2000, "author_id": 999},
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_book(self) -> None:
        author = self.client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()
        book = self.client.post(
            "/api/books",
            json={
                "title": "The Dispossessed",
                "published_year": 1974,
                "author_id": author["id"],
            },
        ).get_json()

        response = self.client.delete(f"/api/books/{book['id']}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get(f"/api/books/{book['id']}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
