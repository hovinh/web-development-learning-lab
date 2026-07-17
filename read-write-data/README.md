# read-write-data

Practice stage for reading a tabular dataset (CSV) into Python data
structures, reshaping it, writing it back out as JSON, reading that JSON
back in, and finally storing the processed records in a database three
ways: SQLAlchemy's ORM directly, `dataset` (a much lower-boilerplate
wrapper over SQLAlchemy), and MongoDB via `pymongo` — a document store
rather than a relational one.

## The idea

`pokemon.csv` is a flat table: one row per Pokemon, with the six battle
stats (`HP`, `Attack`, `Defense`, `Sp. Atk`, `Sp. Def`, `Speed`) plus
`Total` as separate columns alongside identity fields like `Name` and
`Type 1`.

CSV forces that flat shape, but it isn't how you'd naturally model "a
Pokemon has stats" in a general-purpose data structure. This stage's core
exercise is: read the flat CSV, and *reshape* each row into a dict where
those seven stat columns are grouped under one nested `"stats"` key, e.g.:

```json
{
  "number": 1,
  "name": "Bulbasaur",
  "type_1": "Grass",
  "type_2": "Poison",
  "stats": {
    "total": 318,
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "sp_atk": 65,
    "sp_def": 65,
    "speed": 45
  },
  "generation": 1,
  "generation_release_date": "1996-02-27",
  "legendary": false
}
```

That list of dicts is then serialized to `pokemon.json` and read back, to
practice both directions of `json.dump`/`json.load`.

`generation_release_date` doubles as the datetime-processing exercise:
each generation is looked up against the real-world release date of its
original games (an ISO 8601 `"YYYY-MM-DD"` string), which gets parsed into
an actual `datetime.date` — not just carried around as a string. JSON has
no native date type, so `pokemon.py` has to explicitly convert `date` ->
ISO string on the way out (`write_pokemon_json`'s `default` hook) and ISO
string -> `date` on the way back in (`read_pokemon_json`). That conversion
is the point of the exercise, not incidental plumbing.

`pokemon.csv` was chosen for the SQL side of the exercise too: read the
same processed records into a SQLAlchemy ORM class, insert them into a
database with a `Session`, then query them back out — including a
`WHERE`-style filter — and convert each result row back into the nested
dict shape above, so downstream code can't tell whether a record came
from the CSV, the JSON file, or the database.

The exercise originally called for a MySQL database named `pokedex`.
SQLite has no server process and no separate "create the database" step
the way MySQL does — a SQLite database *is* a single file — so `pokedex`
becomes the filename (`pokedex.db`) instead of a server-side database
name. Swapping SQLite for a real MySQL server later would only mean
changing `models.py`'s `ENGINE_URL`; the ORM class and query code are
database-agnostic.

`dataset_demo.py` does the exact same store/insert/filter/convert steps a
second time, using the [`dataset`](https://dataset.readthedocs.io/) library
instead of SQLAlchemy's ORM directly. `dataset` is itself built on top of
SQLAlchemy Core, but trades away an explicit `Pokemon` class and schema
declaration for plain dicts: a table's columns are inferred from whatever
dict you first insert, and filtering is `table.find(generation=1,
legendary=True)` instead of `select(Pokemon).where(...)`. Comparing
`models.py`/`main.py` against `dataset_store.py`/`dataset_demo.py` side by
side is the point — same result, far less ceremony, at the cost of the
type safety and explicitness an ORM class gives you.

`dataset_demo.py` finishes by "freezing" the filtered query result
straight to `gen_1_legendaries.csv` and `.json` via
`freeze_to_csv`/`freeze_to_json` in `dataset_store.py`. Older `dataset`
versions shipped this as a built-in `dataset.freeze()` convenience
function; see "Notes on `dataset`" below for why this stage hand-rolls it
instead of using that function directly.

`mongo_demo.py` runs the same store/insert/filter/convert exercise a
third time, against MongoDB instead of a SQL database. MongoDB is a
*document* store, so this version is the odd one out in a useful way: the
nested `"stats"` dict doesn't need flattening the way it does for
`models.py`/`dataset_store.py` — a MongoDB document stores it as-is. The
one thing that still needs converting by hand is `generation_release_date`,
since BSON (MongoDB's storage format) has a `datetime` type but no
date-only type, the same kind of gap JSON has (see `mongo_store.py`).

## Choosing an approach

Three implementations of the same store/query/convert exercise, for
comparison — not because a real project would pick one at random. Some
guidance on when each is actually the right call:

| | SQLAlchemy ORM (`models.py`) | `dataset` (`dataset_store.py`) | MongoDB (`mongo_store.py`) |
|---|---|---|---|
| Reach for it when... | the project is long-lived, the schema is known and stable, and you want the database to catch mistakes (wrong type, missing column) at write time | it's a script, a one-off data-wrangling task, or a prototype where the schema will keep changing and writing/maintaining ORM classes is pure overhead | the data doesn't naturally fit uniform rows — records vary in shape, nest deeply, or the nesting itself (like `"stats"` here) is what you want to query on |
| Cost | most setup: a class per table, explicit column types, a migration story (e.g. Alembic) for schema changes | least type safety: a typo'd dict key silently becomes a `NULL`/missing field instead of an error | easiest to let structure drift over time, since nothing enforces two documents in the same collection look alike |
| This dataset specifically | the natural fit — every Pokemon genuinely has the same fields, which is exactly what a fixed relational schema is for | reasonable for a quick analysis script over `pokemon.csv` you don't intend to maintain | overkill *as modeled here* — the nesting only exists because the exercise asked for it; real Pokemon data doesn't vary enough per-record to need a schemaless store |

The honest takeaway from building all three against the same data: this
dataset is relational at heart (uniform columns, one type per field), so
`models.py`'s explicit schema is the most defensible real-world choice;
`dataset` is worth it purely for iteration speed on throwaway scripts;
and MongoDB earns its keep only when records genuinely don't share a
shape — think user-submitted forms with optional fields, event logs with
varying payloads, or content with deeply nested, query-relevant structure
— none of which describes a Pokedex.

## Files

- `pokemon.csv` — the source dataset: 800 Pokemon (Gen 1–6), from the
  widely-used [armgilles/pokemon.csv](https://gist.github.com/armgilles/194bcff35001e7eb53a2a8b441e8b2c6) gist.
- `pokemon.py` — CSV/JSON conversion helpers: `read_pokemon_csv`,
  `write_pokemon_json`, `read_pokemon_json`.
- `models.py` — the SQLAlchemy side: the `Pokemon` ORM class (flat
  columns — no nested "stats" column type exists in SQL), `get_engine()`,
  and `pokemon_from_dict`/`pokemon_to_dict` converters to/from the
  nested-dict shape used everywhere else in this stage.
- `main.py` — entry point/demo: runs the full pipeline (CSV → dicts →
  JSON → dicts → SQLite via SQLAlchemy → filtered query → dicts).
- `dataset_store.py` — the `dataset` equivalent of `models.py`:
  `pokemon_to_row`/`row_to_pokemon` converters and `get_pokemon_table()`.
  No ORM class, since `dataset` doesn't use one.
- `dataset_demo.py` — entry point/demo for the `dataset` version: CSV →
  dicts → SQLite via `dataset` → filtered query → dicts → frozen
  CSV/JSON files.
- `mongo_store.py` — the MongoDB equivalent of `models.py`/
  `dataset_store.py`: `pokemon_to_document`/`document_to_pokemon`
  converters and `get_pokemon_collection()`. No flattening logic, unlike
  the SQL versions — see "The idea" above.
- `mongo_demo.py` — entry point/demo for the MongoDB version: CSV →
  dicts → MongoDB via `pymongo` → filtered query → dicts. Requires a
  MongoDB server; see "Running" below.
- `pokemon.json`, `pokedex.db`, `pokedex_dataset.db`,
  `gen_1_legendaries.csv`, `gen_1_legendaries.json` — all generated by
  running `main.py`/`dataset_demo.py`; not committed (see root
  `.gitignore`) since they're fully reproducible from `pokemon.csv`.
  MongoDB's data lives in the MongoDB server itself, not a file in this
  folder, so there's nothing to gitignore for `mongo_demo.py`.

## Notes on the CSV → dict conversion

- Every value read via `csv.DictReader` comes back as a **string** — the
  script explicitly converts stat columns and `Generation` to `int`, and
  `Legendary` (`"True"`/`"False"`) to `bool`. This is the main thing to
  internalize: CSV has no types, JSON (and Python) does, so that
  conversion step is not optional busywork, it's the point.
- `Type 2` is blank in the CSV for single-type Pokemon (e.g. Charmander is
  `Fire` with no second type). Blank strings are converted to `None`
  rather than kept as `""`, since "no second type" is better modeled as
  the absence of a value.

## Notes on the SQLAlchemy model

- `Pokemon.id` (not `Pokemon.number`) is the primary key. The Pokedex
  `number` looks like the obvious choice, but it isn't unique in this
  dataset — Mega Evolutions (e.g. `MewtwoMega Mewtwo X`) reuse their base
  form's number. A separate auto-incrementing `id` is the safe choice
  whenever the "natural" key can repeat.
- `get_engine()` drops and recreates the `pokemon` table on every call, so
  running `main.py` repeatedly doesn't keep re-inserting the same 800 rows
  — this is a learning demo, not a database meant to persist across runs.
- The filtered query (`session.scalars(select(Pokemon).where(...))`) uses
  SQLAlchemy 2.0's `select()`-style API rather than the older
  `session.query(...)` — it's the currently recommended style and reads
  closer to the SQL it generates.

## Notes on `dataset`

- `dataset` infers each column's type from the *first* row it sees for a
  new table, then builds the table from that. There's no equivalent of
  `models.py`'s explicit column declarations — which is the whole appeal,
  but also means a typo'd or missing key in one row's dict silently
  becomes a `NULL` rather than a `TypeError` at write time the way an ORM
  class would catch it.
- `table.insert_many()` needs an actual `list`, not a generator —
  `dataset_demo.py` builds one with a list comprehension. Passed a
  generator, `insert_many()` silently inserts nothing and raises no
  error; this was caught by noticing the row count came back as `0` and
  is exactly the kind of surprise you trade explicitness for when a
  library removes boilerplate.
- `table.find(**kwargs)` only expresses equality filters (`AND`-ed
  together). Anything more complex (`OR`, ranges, joins) drops down to
  `db.query(sql)` with a hand-written SQL string — `dataset` optimizes for
  the common case, not full expressiveness.
- `dataset.freeze()` — the built-in convenience for dumping a query
  result to CSV/JSON — isn't usable today. As of `dataset` 1.0, that
  functionality was split into a separate `datafreeze` package, which is
  now abandoned (last released in 2016) and fails to even import: it's
  missing a dependency (`normality`) it never declared. Rather than
  depend on something broken, `dataset_store.py` reimplements the same
  convenience in ~15 lines: a `dataset` query result is already a list of
  flat dicts with matching keys, which is exactly what
  `csv.DictWriter`/`json.dump` want.

## Notes on MongoDB / pymongo

- No flattening step: `pokemon_to_document()` stores the nested `"stats"`
  dict as-is. This is the main thing this version demonstrates — a
  document database's schema is "whatever shape your document already
  is," where a relational table forces every value into its own column.
- MongoDB auto-generates an `_id` field (an `ObjectId`) for every document
  that doesn't specify one — the document equivalent of `models.py`'s
  auto-incrementing `id` primary key, for the same reason (the Pokedex
  `number` isn't unique; Mega Evolutions share their base form's number).
  `document_to_pokemon()` drops it, same as the SQL versions drop their
  own auto-generated ID.
- BSON, MongoDB's storage format, has a `datetime` type but no date-only
  type — the same gap JSON has, just with a different workaround.
  `pokemon_to_document()` combines the `date` with midnight
  (`datetime.combine(date, datetime.min.time())`) on the way in;
  `document_to_pokemon()` calls `.date()` on the way back out.
- `collection.find({...})` takes a query *document*, not keyword
  arguments — `{"generation": 1, "legendary": True}` matches `dataset`'s
  `table.find(generation=1, legendary=True)` for a simple equality
  filter, but MongoDB's query language extends much further from that
  same dict shape (`{"$gt": ...}`, `{"$or": [...]}`, matching into nested
  fields) without ever dropping to a separate query string.
- This version was verified against
  [`mongomock`](https://github.com/mongomock/mongomock) (an in-memory
  pymongo-API-compatible stand-in) rather than a real server, since no
  MongoDB instance was running in the environment this was written in.
  The code talks to `pymongo.MongoClient` the same way either way — see
  "Running" below for how to point it at a real server.

## Running

Add the new dependency first, if you haven't already synced the venv:

```bash
.venv/Scripts/python.exe -m piptools sync requirements.txt
```

Then, from the repo root with `.venv` active:

```bash
python read-write-data/main.py
python read-write-data/dataset_demo.py
```

`mongo_demo.py` additionally needs a MongoDB server reachable at
`mongodb://localhost:27017` (see `mongo_store.MONGO_URI`). If you don't
already have MongoDB installed, the quickest way to get one running
locally is Docker:

```bash
docker run -d -p 27017:27017 --name mongodb mongo
```

Then:

```bash
python read-write-data/mongo_demo.py
```
