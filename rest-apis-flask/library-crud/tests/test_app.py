"""CRUD tests for app.py's Author and Book routes.

Uses Flask's `test_client()` against an isolated, temporary SQLite
database per test (via the `client` fixture) - no live server/port
needed, same approach as
dataviz-python-js/data-serve/tests/test_app.py.
"""

import pytest

from app import create_app
from models import db


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(sqlite_uri=f"sqlite:///{db_path}")
    app.config["TESTING"] = True
    return app.test_client()


# ---- Authors ----


def test_create_and_get_author(client) -> None:
    response = client.post("/api/authors", json={"name": "Ursula K. Le Guin"})
    assert response.status_code == 201
    author = response.get_json()
    assert author["name"] == "Ursula K. Le Guin"
    assert author["books"] == []

    response = client.get(f"/api/authors/{author['id']}")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Ursula K. Le Guin"


def test_create_author_missing_name_is_422(client) -> None:
    # flask-smorest's @blp.arguments(AuthorSchema) validates the body
    # before create_author() ever runs - a schema mismatch returns 422
    # (Unprocessable Entity) with Marshmallow's own field errors nested
    # under "errors"/"json", not the raw {"name": [...]} shape a plain
    # marshmallow ValidationError.messages would give.
    response = client.post("/api/authors", json={})
    assert response.status_code == 422
    assert "name" in response.get_json()["errors"]["json"]


def test_create_author_blank_name_is_422(client) -> None:
    response = client.post("/api/authors", json={"name": ""})
    assert response.status_code == 422
    assert "name" in response.get_json()["errors"]["json"]


def test_list_authors(client) -> None:
    client.post("/api/authors", json={"name": "Ursula K. Le Guin"})
    client.post("/api/authors", json={"name": "Octavia E. Butler"})

    response = client.get("/api/authors")
    assert response.status_code == 200
    names = {author["name"] for author in response.get_json()}
    assert names == {"Ursula K. Le Guin", "Octavia E. Butler"}


def test_update_author(client) -> None:
    created = client.post("/api/authors", json={"name": "Typo Namee"}).get_json()

    response = client.put(f"/api/authors/{created['id']}", json={"name": "Correct Name"})
    assert response.status_code == 200
    assert response.get_json()["name"] == "Correct Name"


def test_delete_author_cascades_to_their_books(client) -> None:
    author = client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()
    book = client.post(
        "/api/books",
        json={"title": "The Left Hand of Darkness", "published_year": 1969, "author_id": author["id"]},
    ).get_json()

    response = client.delete(f"/api/authors/{author['id']}")
    assert response.status_code == 204

    assert client.get(f"/api/authors/{author['id']}").status_code == 404
    # The cascade in models.py's Author.books relationship should have
    # removed the book too, not just orphaned it.
    assert client.get(f"/api/books/{book['id']}").status_code == 404


def test_get_unknown_author_is_404(client) -> None:
    assert client.get("/api/authors/999").status_code == 404


# ---- Books ----


def test_create_and_get_book(client) -> None:
    author = client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()

    response = client.post(
        "/api/books",
        json={"title": "The Dispossessed", "published_year": 1974, "author_id": author["id"]},
    )
    assert response.status_code == 201
    book = response.get_json()
    assert book["title"] == "The Dispossessed"
    assert book["author"]["name"] == "Ursula K. Le Guin"

    response = client.get(f"/api/books/{book['id']}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "The Dispossessed"


def test_create_book_with_unknown_author_is_400(client) -> None:
    # Unlike a schema-shape failure (422 above), this one passes schema
    # validation - author_id is a well-formed int - and is instead
    # rejected by resources/books.py's own _check_author_exists() check,
    # which uses flask_smorest.abort(400, ...) directly.
    response = client.post(
        "/api/books",
        json={"title": "Orphan Book", "published_year": 2000, "author_id": 999},
    )
    assert response.status_code == 400


def test_create_book_missing_fields_is_422(client) -> None:
    response = client.post("/api/books", json={"title": "No Year Or Author"})
    assert response.status_code == 422
    errors = response.get_json()["errors"]["json"]
    assert "published_year" in errors
    assert "author_id" in errors


def test_new_book_appears_nested_under_its_author(client) -> None:
    author = client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()
    client.post(
        "/api/books",
        json={"title": "The Dispossessed", "published_year": 1974, "author_id": author["id"]},
    )

    response = client.get(f"/api/authors/{author['id']}")
    titles = [book["title"] for book in response.get_json()["books"]]
    assert titles == ["The Dispossessed"]


def test_update_book(client) -> None:
    author = client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()
    book = client.post(
        "/api/books",
        json={"title": "Typo Title", "published_year": 1974, "author_id": author["id"]},
    ).get_json()

    response = client.put(
        f"/api/books/{book['id']}",
        json={"title": "The Dispossessed", "published_year": 1974, "author_id": author["id"]},
    )
    assert response.status_code == 200
    assert response.get_json()["title"] == "The Dispossessed"


def test_delete_book(client) -> None:
    author = client.post("/api/authors", json={"name": "Ursula K. Le Guin"}).get_json()
    book = client.post(
        "/api/books",
        json={"title": "The Dispossessed", "published_year": 1974, "author_id": author["id"]},
    ).get_json()

    response = client.delete(f"/api/books/{book['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/books/{book['id']}").status_code == 404


def test_get_unknown_book_is_404(client) -> None:
    assert client.get("/api/books/999").status_code == 404
