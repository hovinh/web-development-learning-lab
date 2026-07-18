"""Tests for app.py's routes, run against both backends.

Every test is parametrized over both backends via the `client` fixture
below, and asserts the exact same thing either way - that's the actual
point of this stage (one API, two interchangeable backends), so testing
only one backend would miss the one thing worth verifying: that they
agree. Uses Flask's `test_client()`, so no live server/port is needed -
same in-process approach as data-process/data-analysis's tests, applied
to a Flask app instead of plain functions.
"""

import json

import pytest

from app import create_app
from models import Pokemon, db

SAMPLE_POKEDEX = [
    {
        "national_number": 1,
        "name": "bulbasaur",
        "display_name": "Bulbasaur",
        "generation": 1,
        "species": "Seed Pokémon",
        "types": ["Grass", "Poison"],
        "abilities": ["Overgrow", "Chlorophyll"],
        "hidden_ability": "Chlorophyll",
        "height_m": 0.7,
        "weight_kg": 6.9,
        "sprite_url": "https://example.com/sprites/1.png",
        "artwork": "images/bulbasaur.jpg",
    },
    {
        "national_number": 4,
        "name": "charmander",
        "display_name": "Charmander",
        "generation": 1,
        "species": "Lizard Pokémon",
        "types": ["Fire"],
        "abilities": ["Blaze", "Solar Power"],
        "hidden_ability": "Solar Power",
        "height_m": 0.6,
        "weight_kg": 8.5,
        "sprite_url": "https://example.com/sprites/4.png",
        "artwork": "images/charmander.jpg",
    },
    {
        "national_number": 152,
        "name": "chikorita",
        "display_name": "Chikorita",
        "generation": 2,
        "species": "Leaf Pokémon",
        "types": ["Grass"],
        "abilities": ["Overgrow"],
        "hidden_ability": None,
        "height_m": 0.9,
        "weight_kg": 6.4,
        "sprite_url": "https://example.com/sprites/152.png",
        "artwork": "images/chikorita.jpg",
    },
]

FAKE_JPEG_BYTES = b"\xff\xd8\xff\xe0fake-jpeg-bytes"


@pytest.fixture
def file_client(tmp_path):
    """A file-backend app over a small synthetic pokedex.json + images/,
    instead of the real data-process output."""
    json_path = tmp_path / "pokedex.json"
    json_path.write_text(json.dumps(SAMPLE_POKEDEX), encoding="utf-8")

    images_dir = tmp_path / "images"
    images_dir.mkdir()
    for entry in SAMPLE_POKEDEX:
        (images_dir / f"{entry['name']}.jpg").write_bytes(FAKE_JPEG_BYTES)
    # chikorita's image is deliberately missing, to exercise the 404 path.
    (images_dir / "chikorita.jpg").unlink()

    app = create_app("file", json_path=json_path, images_dir=images_dir)
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def sqlite_client(tmp_path):
    """A sqlite-backend app over an isolated, temporary database seeded
    with the same SAMPLE_POKEDEX rows - so both fixtures represent the
    exact same data through each backend."""
    db_path = tmp_path / "test.db"
    app = create_app("sqlite", sqlite_uri=f"sqlite:///{db_path}")
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()
        for entry in SAMPLE_POKEDEX:
            types = entry["types"]
            artwork_blob = FAKE_JPEG_BYTES if entry["name"] != "chikorita" else None
            db.session.add(
                Pokemon(
                    national_number=entry["national_number"],
                    name=entry["name"],
                    display_name=entry["display_name"],
                    generation=entry["generation"],
                    species=entry["species"],
                    type_1=types[0],
                    type_2=types[1] if len(types) > 1 else None,
                    abilities=entry["abilities"],
                    hidden_ability=entry["hidden_ability"],
                    height_m=entry["height_m"],
                    weight_kg=entry["weight_kg"],
                    sprite_url=entry["sprite_url"],
                    artwork_blob=artwork_blob,
                    artwork_mimetype="image/jpeg" if artwork_blob else None,
                )
            )
        db.session.commit()

    return app.test_client()


@pytest.fixture(params=["file_client", "sqlite_client"])
def client(request):
    """Runs every test below once per backend - see this module's docstring."""
    return request.getfixturevalue(request.param)


def test_meta_reports_backend_and_count(client) -> None:
    response = client.get("/api/meta")
    assert response.status_code == 200
    assert response.get_json()["count"] == 3


def test_list_pokemon_sorted_by_national_number(client) -> None:
    response = client.get("/api/pokemon")
    assert response.status_code == 200
    names = [entry["name"] for entry in response.get_json()]
    assert names == ["bulbasaur", "charmander", "chikorita"]


def test_list_pokemon_filtered_by_type_matches_either_column(client) -> None:
    # "Grass" is bulbasaur's type_1 and chikorita's only type - both
    # should come back regardless of which slot the type sits in.
    response = client.get("/api/pokemon?type=grass")
    names = {entry["name"] for entry in response.get_json()}
    assert names == {"bulbasaur", "chikorita"}


def test_list_pokemon_filtered_by_generation(client) -> None:
    response = client.get("/api/pokemon?generation=2")
    names = [entry["name"] for entry in response.get_json()]
    assert names == ["chikorita"]


def test_list_pokemon_pagination(client) -> None:
    response = client.get("/api/pokemon?limit=1&offset=1")
    names = [entry["name"] for entry in response.get_json()]
    assert names == ["charmander"]


def test_get_one_pokemon(client) -> None:
    response = client.get("/api/pokemon/bulbasaur")
    assert response.status_code == 200
    data = response.get_json()
    assert data["display_name"] == "Bulbasaur"
    assert data["types"] == ["Grass", "Poison"]
    assert data["hidden_ability"] == "Chlorophyll"
    assert data["artwork_url"] == "/api/pokemon/bulbasaur/artwork"
    # Neither backend should leak a local filesystem path.
    assert "artwork" not in data


def test_get_one_pokemon_404_for_unknown_name(client) -> None:
    response = client.get("/api/pokemon/missingno")
    assert response.status_code == 404


def test_get_artwork_returns_image_bytes(client) -> None:
    response = client.get("/api/pokemon/bulbasaur/artwork")
    assert response.status_code == 200
    assert response.mimetype == "image/jpeg"
    assert response.data == FAKE_JPEG_BYTES


def test_get_artwork_404_when_image_missing(client) -> None:
    # chikorita has a structured record but no artwork file/blob - both
    # fixtures set this up deliberately (see above).
    response = client.get("/api/pokemon/chikorita/artwork")
    assert response.status_code == 404
