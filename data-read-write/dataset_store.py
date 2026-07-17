"""Store/query the processed Pokemon records using the `dataset` library
-- a thin wrapper over SQLAlchemy Core that trades explicit ORM classes
and schema declarations for plain dicts and a much smaller API.

Compare with models.py, which does the same job with SQLAlchemy's ORM
directly: a `Pokemon` class, explicit `Mapped`/column declarations, and
`select()` + `Session` for querying. Here there's no class and no schema
declaration at all -- `dataset` creates the table and infers each column's
type automatically from the first dict it's given.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

import dataset

# A separate database file from models.py's pokedex.db -- both represent
# the same data, but keeping them apart avoids any confusion about which
# library/approach produced a given file.
DB_PATH = Path(__file__).parent / "pokedex_dataset.db"
DB_URL = f"sqlite:///{DB_PATH}"


def pokemon_to_row(data: dict[str, Any]) -> dict[str, Any]:
    """Flatten a nested Pokemon dict (as produced by
    pokemon.read_pokemon_csv()) into the flat dict `dataset` stores as one
    table row. Same reasoning as models.py's pokemon_from_dict(): a
    relational table has no nested-column type, so "stats" has to be
    unpacked into individual keys before it can be stored.
    """
    stats = data["stats"]
    return {
        "number": data["number"],
        "name": data["name"],
        "type_1": data["type_1"],
        "type_2": data["type_2"],
        "total": stats["total"],
        "hp": stats["hp"],
        "attack": stats["attack"],
        "defense": stats["defense"],
        "sp_atk": stats["sp_atk"],
        "sp_def": stats["sp_def"],
        "speed": stats["speed"],
        "generation": data["generation"],
        "generation_release_date": data["generation_release_date"],
        "legendary": data["legendary"],
    }


def row_to_pokemon(row: dict[str, Any]) -> dict[str, Any]:
    """Un-flatten a row dict read back from the database into the same
    nested-dict shape used elsewhere in this stage -- the inverse of
    pokemon_to_row(). `dataset` also adds its own auto-increment "id"
    column to every row, which is dropped here since it isn't part of
    that shape.
    """
    return {
        "number": row["number"],
        "name": row["name"],
        "type_1": row["type_1"],
        "type_2": row["type_2"],
        "stats": {
            "total": row["total"],
            "hp": row["hp"],
            "attack": row["attack"],
            "defense": row["defense"],
            "sp_atk": row["sp_atk"],
            "sp_def": row["sp_def"],
            "speed": row["speed"],
        },
        "generation": row["generation"],
        "generation_release_date": row["generation_release_date"],
        "legendary": row["legendary"],
    }


def get_pokemon_table(db: dataset.Database) -> dataset.Table:
    """Return the `pokemon` table, dropping it first if it already exists.

    `dataset` creates a table automatically on first insert -- there's no
    schema to declare up front. Dropping it first just keeps the demo
    re-runnable, so running dataset_demo.py twice doesn't insert the same
    800 rows on top of themselves (same reasoning as models.get_engine()).
    """
    if "pokemon" in db.tables:
        db["pokemon"].drop()
    return db["pokemon"]


# `dataset` used to ship a freeze() convenience function for dumping a
# query result straight to CSV/JSON. As of dataset 1.0, that was split
# out into a separate `datafreeze` package -- which is now abandoned
# (last released in 2016) and doesn't even import cleanly (it's missing
# a dependency it never declared). Rather than depend on that, these two
# functions provide the same convenience by hand: a `dataset` query
# result is already a list of flat dicts with matching keys, which is
# exactly what csv.DictWriter/json.dump want, so there's very little to
# hand-roll.


def freeze_to_csv(rows: list[dict[str, Any]], csv_path: Path) -> None:
    """Write a `dataset` query result straight to a CSV file."""
    if not rows:
        raise ValueError("Cannot freeze an empty result to CSV: no columns to write")

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        # Every row from a `dataset` query has the same keys (the table's
        # columns), so the first row's keys are a safe source of headers.
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _json_default(value: Any) -> str:
    """`default` hook for json.dump -- same reasoning as
    pokemon._json_default(): JSON has no date type, so a `date` value is
    converted to its ISO 8601 string form."""
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def freeze_to_json(rows: list[dict[str, Any]], json_path: Path) -> None:
    """Write a `dataset` query result straight to a JSON file."""
    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(rows, json_file, indent=2, default=_json_default)
