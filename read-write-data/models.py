"""SQLAlchemy ORM model for storing processed Pokemon records in a
file-based SQLite database.

pokemon.py works with nested dicts (stats grouped under a "stats" key,
suited to JSON). A relational table has no such nested-column concept --
every column holds one flat, scalar value. This module defines that flat
`Pokemon` table, plus two small converters (`pokemon_from_dict`,
`pokemon_to_dict`) so the rest of the stage can keep using the nested-dict
shape without caring whether a record came from the CSV, the JSON file,
or the database.

The exercise originally called for a MySQL database named "pokedex".
SQLite has no server process and no separate "create the database" step
the way MySQL does -- a SQLite database *is* a single file on disk -- so
"pokedex" becomes the filename (pokedex.db) instead of a server-side
database name.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DB_PATH = Path(__file__).parent / "pokedex.db"
ENGINE_URL = f"sqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    """Base class every ORM model inherits from; SQLAlchemy uses it to
    collect table metadata for create_all()/drop_all()."""


class Pokemon(Base):
    """One row per Pokemon. Battle stats are flattened into individual
    columns -- there is no nested/dict column type in a relational table,
    unlike the JSON representation in pokemon.py."""

    __tablename__ = "pokemon"

    # The Pokedex `number` looks like an obvious primary key, but it isn't
    # unique in this dataset: Mega Evolutions (e.g. "VenusaurMega Venusaur")
    # reuse their base form's number. A separate auto-incrementing `id` is
    # the safe, conventional choice when the "natural" key can repeat.
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[int]
    name: Mapped[str] = mapped_column(String(50))
    type_1: Mapped[str] = mapped_column(String(20))
    type_2: Mapped[str | None] = mapped_column(String(20))

    total: Mapped[int]
    hp: Mapped[int]
    attack: Mapped[int]
    defense: Mapped[int]
    sp_atk: Mapped[int]
    sp_def: Mapped[int]
    speed: Mapped[int]

    generation: Mapped[int]
    # SQLAlchemy's default type map already knows datetime.date -> Date,
    # so no explicit mapped_column() type is needed here.
    generation_release_date: Mapped[date]
    legendary: Mapped[bool]

    def __repr__(self) -> str:
        return f"Pokemon(id={self.id!r}, number={self.number!r}, name={self.name!r})"


def get_engine() -> Engine:
    """Create the engine for the file-based SQLite database, (re)creating
    the `pokemon` table.

    The table is dropped before being recreated so re-running the stage's
    demo doesn't keep inserting the same 800 rows on top of themselves --
    this is a learning demo, not a database that needs to persist data
    across runs.
    """
    engine = create_engine(ENGINE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return engine


def pokemon_from_dict(data: dict[str, Any]) -> Pokemon:
    """Build a Pokemon ORM instance from the nested-dict shape produced by
    pokemon.read_pokemon_csv()/read_pokemon_json() -- the inverse of
    pokemon_to_dict() below."""
    stats = data["stats"]
    return Pokemon(
        number=data["number"],
        name=data["name"],
        type_1=data["type_1"],
        type_2=data["type_2"],
        total=stats["total"],
        hp=stats["hp"],
        attack=stats["attack"],
        defense=stats["defense"],
        sp_atk=stats["sp_atk"],
        sp_def=stats["sp_def"],
        speed=stats["speed"],
        generation=data["generation"],
        generation_release_date=data["generation_release_date"],
        legendary=data["legendary"],
    )


def pokemon_to_dict(pokemon: Pokemon) -> dict[str, Any]:
    """Convert a Pokemon ORM row back into the same nested-dict shape used
    by pokemon.py, with stats grouped under "stats" -- the inverse of
    pokemon_from_dict() above."""
    return {
        "number": pokemon.number,
        "name": pokemon.name,
        "type_1": pokemon.type_1,
        "type_2": pokemon.type_2,
        "stats": {
            "total": pokemon.total,
            "hp": pokemon.hp,
            "attack": pokemon.attack,
            "defense": pokemon.defense,
            "sp_atk": pokemon.sp_atk,
            "sp_def": pokemon.sp_def,
            "speed": pokemon.speed,
        },
        "generation": pokemon.generation,
        "generation_release_date": pokemon.generation_release_date,
        "legendary": pokemon.legendary,
    }
