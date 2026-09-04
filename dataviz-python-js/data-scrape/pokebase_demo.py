"""Concept: a dedicated API client library, instead of raw requests+JSON.

`requests_basics.py` calls PokeAPI directly: build the URL, call
`requests.get`, call `.json()`, and know the exact shape of the response
dict (e.g. `pokemon["types"][0]["type"]["name"]`) well enough to pull
fields back out of it. `pokebase` (https://github.com/PokeAPI/pokebase)
is a small third-party library built specifically for PokeAPI: it knows
the endpoint URLs and response shapes already, so calling code works with
Python objects and attributes (`pokemon.types[0].type.name`) instead of
raw dicts.

This is the general trade-off of a "library API" wrapper around a REST
API: less code and no need to memorize the JSON shape, at the cost of a
dependency that has to keep up with the underlying API, and one more
layer to look through when something doesn't behave as expected.

pokebase also caches every response to disk on its own (a separate,
simpler mechanism than requests-cache - see cached_requests_demo.py),
which is why calling get_pokemon_via_library() twice in a row is fast
the second time without this module doing anything extra to arrange it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pokebase

STAGE_DIR = Path(__file__).parent

# pokebase caches API responses to disk itself (see pokebase/cache.py);
# by default that's a shared, cross-project location under the user's
# home directory. Pointing it at a folder inside this stage keeps the
# cache (and what it demonstrates) local to this repo. This must run
# before any pokebase.* call, per pokebase's own documentation.
pokebase.cache.set_cache(str(STAGE_DIR / "pokebase_cache"))


def get_pokemon_via_library(name_or_id: str | int) -> pokebase.APIResource:
    """Fetch a Pokemon resource through pokebase instead of raw HTTP.

    Returns pokebase's own `APIResource` wrapper object rather than a
    dict - summarize_via_library() below shows how attribute access
    compares to the dict indexing in requests_basics.summarize().
    """
    return pokebase.pokemon(name_or_id)


def summarize_via_library(pokemon: pokebase.APIResource) -> dict[str, Any]:
    """The pokebase equivalent of requests_basics.summarize().

    Same output shape as the other three sources in this stage, built
    from attribute access instead of dict keys - e.g. `pokemon.types`
    instead of `pokemon["types"]`.
    """
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "height_dm": pokemon.height,
        "weight_hg": pokemon.weight,
        "types": [entry.type.name for entry in pokemon.types],
        "abilities": [entry.ability.name for entry in pokemon.abilities],
        "sprite_url": pokemon.sprites.front_default,
    }


if __name__ == "__main__":
    pikachu = get_pokemon_via_library("pikachu")
    for key, value in summarize_via_library(pikachu).items():
        print(f"{key}: {value}")
