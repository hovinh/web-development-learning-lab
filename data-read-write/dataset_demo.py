"""Entry point / demo for the `dataset` version of the SQL example.

Same exercise as the SQLAlchemy ORM steps in main.py -- store the
processed Pokemon records in a SQLite database, query them back with a
filter, convert the result back to dicts -- but using the `dataset`
library instead, to compare how much boilerplate it removes: no ORM
class, no schema declaration, no Session/select() ceremony.
"""

from __future__ import annotations

from pathlib import Path

import dataset

from dataset_store import (
    DB_URL,
    freeze_to_csv,
    freeze_to_json,
    get_pokemon_table,
    pokemon_to_row,
    row_to_pokemon,
)
from pokemon import read_pokemon_csv

STAGE_DIR = Path(__file__).parent
CSV_PATH = STAGE_DIR / "pokemon.csv"
FROZEN_CSV_PATH = STAGE_DIR / "gen_1_legendaries.csv"
FROZEN_JSON_PATH = STAGE_DIR / "gen_1_legendaries.json"


def main() -> None:
    # Step 1: CSV -> list of dicts, with stats nested (same as main.py).
    pokemon_list = read_pokemon_csv(CSV_PATH)
    print(f"Read {len(pokemon_list)} Pokemon from {CSV_PATH.name}")

    # Step 2: store them. `dataset.connect()` opens the SQLite file (and
    # creates it if it doesn't exist yet) -- no engine/Session setup.
    db = dataset.connect(DB_URL)
    table = get_pokemon_table(db)

    # insert_many() takes plain dicts directly -- no ORM instances to
    # construct, and no pre-declared columns; `dataset` infers each
    # column's type from the values in these rows the first time it sees
    # them. Note: it needs an actual list here, not a generator -- passed
    # a generator, it silently inserts nothing.
    table.insert_many([pokemon_to_row(data) for data in pokemon_list])
    print(f"Inserted {len(pokemon_list)} Pokemon into {DB_URL}")

    # Step 3: query with a filter. `table.find(**kwargs)` builds the
    # equivalent of a SQL `WHERE column = value AND ...` from keyword
    # arguments -- there's no select()/where() to write by hand.
    gen_1_legendaries = list(table.find(generation=1, legendary=True))

    print(f"\nGeneration 1 legendaries ({len(gen_1_legendaries)}):")
    for row in gen_1_legendaries:
        # Convert each flat row back to the nested-dict shape used
        # everywhere else in this stage.
        print(" -", row_to_pokemon(row))

    # Step 4: "freeze" that query result straight to CSV and JSON. This is
    # the convenience `dataset.freeze()` used to provide -- see the
    # comment above freeze_to_csv()/freeze_to_json() in dataset_store.py
    # for why this stage hand-rolls it instead of using that function.
    freeze_to_csv(gen_1_legendaries, FROZEN_CSV_PATH)
    freeze_to_json(gen_1_legendaries, FROZEN_JSON_PATH)
    print(f"\nFroze the query result to {FROZEN_CSV_PATH.name} and {FROZEN_JSON_PATH.name}")


if __name__ == "__main__":
    main()
