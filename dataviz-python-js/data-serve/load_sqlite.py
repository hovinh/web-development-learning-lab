"""Build data-serve/pokedex.db from data-process's pokedex.json + images/.

Run this once before starting the server with the sqlite backend (see
README.md's "Running" section) - `app.py` doesn't build the database
itself, the same way data-process/process_pokedex.py doesn't run
data-scrape/compile_pokedex.py automatically. Keeping "build the data"
and "serve the data" as separate, explicit steps matches every other
multi-stage pipeline already in this repo.

Drops and recreates the table on every run, same reasoning as
data-read-write/models.py's get_engine(): this is a learning demo backed
by data that's fully reproducible from data-process's output, not a
database meant to persist or migrate across runs.
"""

from __future__ import annotations

import json

from app import create_app
from config import IMAGES_DIR, POKEDEX_JSON_PATH
from models import Pokemon, db


def load() -> None:
    if not POKEDEX_JSON_PATH.exists():
        raise FileNotFoundError(
            f"{POKEDEX_JSON_PATH} not found - run data-process/process_pokedex.py first"
        )

    app = create_app("sqlite")

    with app.app_context():
        db.drop_all()
        db.create_all()

        with POKEDEX_JSON_PATH.open(encoding="utf-8") as json_file:
            pokedex = json.load(json_file)

        missing_artwork = 0
        for entry in pokedex:
            image_path = IMAGES_DIR / f"{entry['name']}.jpg"
            if image_path.is_file():
                artwork_blob = image_path.read_bytes()
                artwork_mimetype = "image/jpeg"
            else:
                # Shouldn't happen against data-process's real output
                # (it only ever writes a JSON entry once the matching
                # image exists - see that stage's clean_row()), but
                # handled rather than assumed, since this script could
                # run against a partial/synthetic dataset too.
                artwork_blob = None
                artwork_mimetype = None
                missing_artwork += 1

            types = entry["types"]
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
                    artwork_mimetype=artwork_mimetype,
                )
            )

        db.session.commit()

    print(f"Loaded {len(pokedex)} Pokemon into data-serve/pokedex.db")
    if missing_artwork:
        print(f"  ({missing_artwork} had no artwork file and were stored without one)")


if __name__ == "__main__":
    load()
