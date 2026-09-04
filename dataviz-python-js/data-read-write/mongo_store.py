"""Store/query the processed Pokemon records in MongoDB via pymongo.

Unlike a relational table (models.py, dataset_store.py), MongoDB is a
document store: a document can hold nested structures natively, so the
"stats" sub-dict doesn't need to be flattened into individual fields the
way it does for SQL. The one conversion this module still has to do by
hand is dates: BSON (MongoDB's storage format) has no date-only type,
only a datetime (with a time component), so `generation_release_date`
round-trips through a `datetime.datetime` at midnight rather than staying
a plain `datetime.date`.

Requires a MongoDB server to connect to -- see the stage README for how
to start one locally (e.g. via Docker).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo.collection import Collection
from pymongo.database import Database

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "pokedex"
COLLECTION_NAME = "pokemon"


def get_pokemon_collection(db: Database) -> Collection:
    """Return the `pokemon` collection, dropping it first if it already
    exists. MongoDB creates a collection lazily on first insert -- there's
    no schema to declare up front. Dropping it first just keeps the demo
    re-runnable, same reasoning as models.get_engine()/
    dataset_store.get_pokemon_table()."""
    db.drop_collection(COLLECTION_NAME)
    return db[COLLECTION_NAME]


def pokemon_to_document(data: dict[str, Any]) -> dict[str, Any]:
    """Convert a nested Pokemon dict (as produced by
    pokemon.read_pokemon_csv()) into a MongoDB document.

    This is almost a direct copy -- the nested "stats" dict is stored
    as-is, as a nested document, which is exactly what CSV/SQL couldn't
    do without flattening. The one field that still needs converting is
    the release date, since BSON has no date-only type.
    """
    document = dict(data)
    document["generation_release_date"] = datetime.combine(
        data["generation_release_date"], datetime.min.time()
    )
    return document


def document_to_pokemon(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a MongoDB document back into the same nested-dict shape
    used elsewhere in this stage -- the inverse of pokemon_to_document().

    Drops MongoDB's own auto-generated "_id" field (an ObjectId, not part
    of that shape) and converts the release date's `datetime` back to a
    plain `date`.
    """
    pokemon = {key: value for key, value in document.items() if key != "_id"}
    pokemon["generation_release_date"] = document["generation_release_date"].date()
    return pokemon
