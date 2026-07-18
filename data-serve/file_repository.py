"""The file-based backend: reads data-process's output directly, no
database at all.

`FileRepository` loads pokedex.json once (at construction) into an
in-memory dict keyed by name, and serves each Pokemon's artwork by
reading the corresponding file in images/ straight off disk per request
- there's no caching, no indexing, nothing beyond "the two files
data-process already produced". This is the simplest possible backend
and the natural first thing to reach for when the data is small enough
to fit in memory and doesn't need to be queried in complex ways - see
README.md's "Choosing a backend" for when this stops being true.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Response, send_file


class FileRepository:
    def __init__(self, json_path: Path, images_dir: Path) -> None:
        self._images_dir = images_dir

        with json_path.open(encoding="utf-8") as json_file:
            pokedex = json.load(json_file)

        # Keyed by name for O(1) get_one() lookups; get_all() still has
        # to fall back to a linear scan for filtering (see below) since
        # nothing here is indexed by type/generation the way a real
        # database would be.
        #
        # data-process's own "artwork" field (a local relative path like
        # "images/bulbasaur.jpg") is dropped in favor of "artwork_url" -
        # a path on this stage's own filesystem means nothing to a
        # remote API client, and models.Pokemon.to_dict() produces
        # "artwork_url" only, never "artwork" - dropping it here too is
        # what keeps both backends' JSON shape identical.
        self._pokemon: dict[str, dict[str, Any]] = {
            entry["name"]: {
                key: value for key, value in entry.items() if key != "artwork"
            }
            | {"artwork_url": f"/api/pokemon/{entry['name']}/artwork"}
            for entry in pokedex
        }

    def count(self) -> int:
        return len(self._pokemon)

    def get_all(
        self,
        type_filter: str | None = None,
        generation_filter: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        results = list(self._pokemon.values())

        if type_filter:
            # Case-insensitive: stored types are Title Case ("Fire"), but
            # a query string like ?type=fire is the more natural way to
            # type a URL by hand.
            wanted = type_filter.strip().title()
            results = [entry for entry in results if wanted in entry["types"]]

        if generation_filter is not None:
            results = [entry for entry in results if entry["generation"] == generation_filter]

        # This whole method is an O(n) scan over every Pokemon on every
        # call, no matter the filter - the tradeoff this backend makes
        # for having no database to set up. sqlite_repository.py's
        # equivalent pushes the same filters down into a SQL WHERE
        # clause instead.
        results.sort(key=lambda entry: entry["national_number"])
        return results[offset : offset + limit]

    def get_one(self, name: str) -> dict[str, Any] | None:
        return self._pokemon.get(name)

    def get_artwork_response(self, name: str) -> Response | None:
        if name not in self._pokemon:
            return None

        image_path = self._images_dir / f"{name}.jpg"
        if not image_path.is_file():
            return None

        # send_file (not reading the bytes ourselves) gets conditional
        # GET / range-request support for free - useful even for a small
        # JPEG, and the same reason a real static file server does the
        # same thing rather than reading files by hand.
        return send_file(image_path, mimetype="image/jpeg")
