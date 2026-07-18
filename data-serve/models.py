"""The sqlite backend's schema: one Pokemon row per record, plus its
artwork stored right in the same database.

`db = SQLAlchemy()` is created unbound (no app yet) and wired to a real
Flask app later via `db.init_app(app)` - the standard Flask-SQLAlchemy
pattern, which is what lets the same model/db object serve more than one
Flask app instance (the real server, and each test in tests/test_app.py,
each pointed at its own sqlite file).

## Why type_1/type_2 as flat columns but abilities as a JSON column

Both are lists in data-process/pokedex.json ("types": ["Grass",
"Poison"]), but they get different treatment here:

- `types` is always length 1 or 2 in this dataset (no Pokemon has 3+
  types) - a fixed, small shape is exactly what flat columns are for, so
  this mirrors data-read-write/models.py's own `Pokemon.type_1`/`type_2`
  columns for the exact same reason.
- `abilities` genuinely varies in length (1 to 3 in this dataset) - a
  fixed number of ability columns wouldn't fit as cleanly, and SQLite has
  no native array column type. SQLAlchemy's `JSON` column type is the
  practical middle ground: it stores the list as JSON text under the
  hood but the ORM serializes/deserializes it transparently, so
  `pokemon.abilities` is just a plain Python list on either side.

This split is a small, concrete example of "flat columns fit a fixed
shape; reach for JSON/document-shaped storage once it doesn't" - the
same tension that motivated trying MongoDB for the nested `stats` dict
in data-read-write, just resolved differently here since abilities are
a flat list rather than a nested object.

## Why artwork lives in a BLOB column here (and why that's not the
production answer)

`artwork_blob` stores each Pokemon's full JPEG bytes directly in this
SQLite database, to demonstrate that a relational database *can* hold
unstructured binary data next to structured columns - not because it's
the best way to do it. See README.md's "Notes on storing images in
SQLite vs. production options" for the tradeoffs and why MongoDB (via
GridFS) or plain object storage (S3 and similar) is the better fit once
this needs to run for real.
"""

from __future__ import annotations

from typing import Any

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Pokemon(db.Model):
    __tablename__ = "pokemon"

    id = db.Column(db.Integer, primary_key=True)
    national_number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String, nullable=False)
    generation = db.Column(db.Integer, nullable=False)
    species = db.Column(db.String, nullable=False)
    type_1 = db.Column(db.String, nullable=False)
    type_2 = db.Column(db.String, nullable=True)
    abilities = db.Column(db.JSON, nullable=False)
    hidden_ability = db.Column(db.String, nullable=True)
    height_m = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    sprite_url = db.Column(db.String, nullable=False)
    artwork_blob = db.Column(db.LargeBinary, nullable=True)
    artwork_mimetype = db.Column(db.String, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        """Reassemble the same shape data-process/pokedex.json uses (a
        `types` list, no `type_1`/`type_2`), so API responses look
        identical regardless of which backend produced them - see
        repositories.py's FileRepository for the other half of that
        parity, and tests/test_app.py's parametrized tests that check it.
        """
        types = [self.type_1]
        if self.type_2:
            types.append(self.type_2)

        return {
            "national_number": self.national_number,
            "name": self.name,
            "display_name": self.display_name,
            "generation": self.generation,
            "species": self.species,
            "types": types,
            "abilities": self.abilities,
            "hidden_ability": self.hidden_ability,
            "height_m": self.height_m,
            "weight_kg": self.weight_kg,
            "sprite_url": self.sprite_url,
            "artwork_url": f"/api/pokemon/{self.name}/artwork",
        }
