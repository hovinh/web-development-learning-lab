"""Entry point / demo for the read-write-data stage.

Walks through the full pipeline:
  1. Read the Pokedex CSV into a list of dicts (stats nested).
  2. Write that list out as JSON.
  3. Read the JSON back in, to demonstrate the read side and prove the
     round trip preserved the structure.
  4. Store the processed records in a file-based SQLite database via
     SQLAlchemy's ORM.
  5. Query the database back, including a filter, and convert the result
     back into the same nested-dict shape used in steps 1-3.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import DB_PATH, Pokemon, get_engine, pokemon_from_dict, pokemon_to_dict
from pokemon import read_pokemon_csv, read_pokemon_json, write_pokemon_json

STAGE_DIR = Path(__file__).parent
CSV_PATH = STAGE_DIR / "pokemon.csv"
JSON_PATH = STAGE_DIR / "pokemon.json"


def main() -> None:
    # Step 1: CSV -> list of dicts, with stats nested under "stats".
    pokemon_list = read_pokemon_csv(CSV_PATH)
    print(f"Read {len(pokemon_list)} Pokemon from {CSV_PATH.name}")
    print("First entry:", pokemon_list[0])

    # Step 2: list of dicts -> JSON file.
    write_pokemon_json(pokemon_list, JSON_PATH)
    print(f"\nWrote {JSON_PATH.name}")

    # Step 3: demonstrate reading the JSON back.
    loaded_pokemon_list = read_pokemon_json(JSON_PATH)
    print(f"Read {len(loaded_pokemon_list)} Pokemon back from {JSON_PATH.name}")
    print("First entry (from JSON):", loaded_pokemon_list[0])

    # Sanity check: the round trip (CSV -> dict -> JSON -> dict) should be
    # lossless. This also covers the `date` field: write_pokemon_json()
    # serializes it to an ISO string, and read_pokemon_json() parses that
    # string back into a `date`, so both sides end up with equal `date`
    # objects rather than one being a string and the other a `date`.
    assert pokemon_list == loaded_pokemon_list
    print("\nRound trip verified: CSV -> dict -> JSON -> dict matches.")

    # A quick look at the date handling specifically: a `date` object
    # supports arithmetic and formatting that a plain string doesn't.
    bulbasaur = loaded_pokemon_list[0]
    release_date = bulbasaur["generation_release_date"]
    print(f"\n{bulbasaur['name']}'s generation released on {release_date.isoformat()}")
    print(f"...which is a {type(release_date).__name__}, not a string:", release_date)
    print("...formatted differently:", release_date.strftime("%B %d, %Y"))

    # Step 4: store the processed records in the SQLite database. get_engine()
    # (re)creates the `pokemon` table, so this is safe to re-run.
    engine = get_engine()
    with Session(engine) as session:
        # add_all() stages every new Pokemon row for insert; nothing is
        # written to pokedex.db until commit().
        session.add_all(pokemon_from_dict(data) for data in pokemon_list)
        session.commit()
    print(f"\nInserted {len(pokemon_list)} Pokemon into {DB_PATH.name}")

    # Step 5: query the database back, with a filter -- every Legendary
    # Pokemon from Generation 1 (Articuno, Zapdos, Moltres, Mewtwo, Mew).
    with Session(engine) as session:
        statement = select(Pokemon).where(
            Pokemon.generation == 1, Pokemon.legendary.is_(True)
        )
        gen_1_legendaries = session.scalars(statement).all()

    print(f"\nGeneration 1 legendaries ({len(gen_1_legendaries)}):")
    for pokemon in gen_1_legendaries:
        # Convert each ORM row back to the same nested-dict shape used in
        # steps 1-3, so callers don't need to know the record came from
        # the database rather than the CSV or JSON file.
        print(" -", pokemon_to_dict(pokemon))


if __name__ == "__main__":
    main()
