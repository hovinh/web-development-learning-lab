"""The sqlite backend: queries models.py's Pokemon table instead of
scanning a Python list.

Unlike FileRepository, this one doesn't load anything itself - it
expects load_sqlite.py to have already built data-serve/pokedex.db (see
that script and README.md's "Running" section). `SQLiteRepository`'s
methods only run correctly inside a Flask application context (an
active `with app.app_context():` block, or - automatically - during a
real request), since that's what `Pokemon.query`/`db.session` are scoped
to under Flask-SQLAlchemy.
"""

from __future__ import annotations

from typing import Any

from flask import Response
from sqlalchemy import or_

from models import Pokemon


class SQLiteRepository:
    def count(self) -> int:
        return Pokemon.query.count()

    def get_all(
        self,
        type_filter: str | None = None,
        generation_filter: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        query = Pokemon.query

        if type_filter:
            wanted = type_filter.strip().title()
            # A Pokemon's second type can be null, so this has to check
            # both columns - the same "is it type_1 or type_2" question
            # FileRepository answers with `in entry["types"]` on a list,
            # answered here with a real WHERE ... OR ... clause instead.
            query = query.filter(or_(Pokemon.type_1 == wanted, Pokemon.type_2 == wanted))

        if generation_filter is not None:
            query = query.filter(Pokemon.generation == generation_filter)

        # The database does the filtering, sorting, and pagination here
        # (LIMIT/OFFSET in the generated SQL) - contrast with
        # FileRepository.get_all(), which pulls every row into Python
        # first and slices a list. This is the actual payoff of the
        # sqlite backend over the file one once the dataset is large
        # enough or the query complex enough for that to matter.
        rows = (
            query.order_by(Pokemon.national_number)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [row.to_dict() for row in rows]

    def get_one(self, name: str) -> dict[str, Any] | None:
        row = Pokemon.query.filter_by(name=name).first()
        return row.to_dict() if row else None

    def get_artwork_response(self, name: str) -> Response | None:
        row = Pokemon.query.filter_by(name=name).first()
        if row is None or row.artwork_blob is None:
            return None
        return Response(row.artwork_blob, mimetype=row.artwork_mimetype or "image/jpeg")
