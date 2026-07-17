"""Entry point / demo for the MongoDB version of the SQL examples.

Same exercise as main.py (SQLAlchemy) and dataset_demo.py (`dataset`) --
store the processed Pokemon records, query them back with a filter,
convert the result back to dicts -- but in a document database instead
of a relational one, via pymongo.

Requires a MongoDB server running locally. If you don't already have one,
the quickest way is Docker: `docker run -d -p 27017:27017 --name mongodb
mongo` (see the stage README for details).
"""

from __future__ import annotations

from pathlib import Path

from pymongo import MongoClient

from mongo_store import (
    DB_NAME,
    MONGO_URI,
    document_to_pokemon,
    get_pokemon_collection,
    pokemon_to_document,
)
from pokemon import read_pokemon_csv

CSV_PATH = Path(__file__).parent / "pokemon.csv"


def main() -> None:
    # Step 1: CSV -> list of dicts, with stats nested (same as main.py).
    pokemon_list = read_pokemon_csv(CSV_PATH)
    print(f"Read {len(pokemon_list)} Pokemon from {CSV_PATH.name}")

    # Step 2: store them. Unlike SQLAlchemy/dataset, there's no engine or
    # table/column setup beyond picking a database and collection name --
    # MongoDB creates both lazily on first write.
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = get_pokemon_collection(db)

    collection.insert_many(pokemon_to_document(data) for data in pokemon_list)
    print(f"Inserted {len(pokemon_list)} Pokemon into {DB_NAME}.{collection.name}")

    # Step 3: query with a filter. MongoDB's query documents look similar
    # to `dataset`'s keyword filter at this level of simplicity, but the
    # query language goes much further (comparison/logical operators,
    # matching into nested fields, etc.) without dropping to raw SQL.
    gen_1_legendaries = list(collection.find({"generation": 1, "legendary": True}))

    print(f"\nGeneration 1 legendaries ({len(gen_1_legendaries)}):")
    for document in gen_1_legendaries:
        # Convert each document back to the nested-dict shape used
        # everywhere else in this stage.
        print(" -", document_to_pokemon(document))

    client.close()


if __name__ == "__main__":
    main()
