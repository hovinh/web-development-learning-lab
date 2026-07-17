"""CSV <-> JSON conversion helpers for the Pokedex dataset.

Reads pokemon.csv (a flat row per Pokemon: Name, Type 1, HP, Attack, ...)
into a list of dictionaries where the battle stats (Total, HP, Attack,
Defense, Sp. Atk, Sp. Def, Speed) are grouped under a nested "stats" key,
then can round-trip that structure to and from JSON.

Also demonstrates datetime handling: each Pokemon's generation is looked
up against its real-world release date (an ISO 8601 string, e.g.
"1996-02-27"), parsed into a `datetime.date`. JSON has no native date
type, so the CSV/JSON boundary is where that `date` object and its ISO
string representation get converted back and forth explicitly.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any

# Maps each CSV stat column to the (shorter, JSON-friendly) key it's
# stored under inside the nested "stats" dict.
STAT_COLUMNS: dict[str, str] = {
    "Total": "total",
    "HP": "hp",
    "Attack": "attack",
    "Defense": "defense",
    "Sp. Atk": "sp_atk",
    "Sp. Def": "sp_def",
    "Speed": "speed",
}

# Real-world release date of each Pokemon generation's original games,
# as ISO 8601 strings (the standard, unambiguous "YYYY-MM-DD" format).
GENERATION_RELEASE_DATES: dict[int, str] = {
    1: "1996-02-27",
    2: "1999-11-21",
    3: "2002-11-21",
    4: "2006-09-28",
    5: "2010-09-18",
    6: "2013-10-12",
}


def read_pokemon_csv(csv_path: Path) -> list[dict[str, Any]]:
    """Read the Pokedex CSV into a list of dicts, one per Pokemon.

    Each row's stat columns are grouped under a nested "stats" dict rather
    than left as flat top-level keys, so the shape mirrors how you'd
    naturally model "a Pokemon has stats" in JSON.
    """
    pokemon_list: list[dict[str, Any]] = []

    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        # DictReader uses the header row to key each row by column name,
        # which is far more readable than indexing a plain row by position.
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Build the nested stats dict, converting each value from
            # CSV's string representation to an int along the way.
            stats = {
                json_key: int(row[csv_column])
                for csv_column, json_key in STAT_COLUMNS.items()
            }

            generation = int(row["Generation"])

            pokemon_list.append(
                {
                    "number": int(row["#"]),
                    "name": row["Name"],
                    "type_1": row["Type 1"],
                    # The CSV leaves Type 2 blank for single-type Pokemon;
                    # store that as None rather than an empty string.
                    "type_2": row["Type 2"] or None,
                    "stats": stats,
                    "generation": generation,
                    # Parse the generation's release date from its ISO
                    # string into a real `date` object, so it can be used
                    # for date arithmetic (e.g. "years since release")
                    # rather than staying an opaque string.
                    "generation_release_date": date.fromisoformat(
                        GENERATION_RELEASE_DATES[generation]
                    ),
                    # csv.DictReader gives every value back as a string, so
                    # "True"/"False" needs an explicit conversion to bool.
                    "legendary": row["Legendary"] == "True",
                }
            )

    return pokemon_list


def _json_default(value: Any) -> str:
    """`default` hook for json.dump: called for any value it doesn't know
    how to serialize natively. JSON has no date type, so a `date` object
    is converted to its ISO 8601 string form (e.g. date(1996, 2, 27) ->
    "1996-02-27") -- the standard, unambiguous way to represent a date as
    text.
    """
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def write_pokemon_json(pokemon_list: list[dict[str, Any]], json_path: Path) -> None:
    """Write the list of Pokemon dicts to a JSON file, pretty-printed."""
    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(pokemon_list, json_file, indent=2, default=_json_default)


def read_pokemon_json(json_path: Path) -> list[dict[str, Any]]:
    """Read the Pokemon list back from a JSON file written by
    write_pokemon_json()."""
    with json_path.open(encoding="utf-8") as json_file:
        pokemon_list = json.load(json_file)

    # JSON has no date type, so `generation_release_date` comes back as a
    # plain ISO string ("1996-02-27"). Parse it back into a `date` object
    # to match what read_pokemon_csv() produces -- JSON is a transport
    # format here, not the shape we want to keep working with in Python.
    for pokemon in pokemon_list:
        pokemon["generation_release_date"] = date.fromisoformat(
            pokemon["generation_release_date"]
        )

    return pokemon_list
