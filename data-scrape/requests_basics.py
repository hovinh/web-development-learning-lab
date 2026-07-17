"""Concept: `requests` + a RESTful Web API (PokeAPI, https://pokeapi.co).

PokeAPI is a public REST API: every kind of resource (a Pokemon, a type,
an ability, ...) lives at its own predictable URL, and a plain HTTP GET
returns it as JSON - no authentication, no client library required. This
module is the "just `requests`, nothing else" baseline for this stage;
the other modules build on it or contrast with it:
  - cached_requests_demo.py wraps the same call in requests-cache
  - pokebase_demo.py replaces raw HTTP+JSON with a dedicated client library
  - pokemondb_scraper.py shows the opposite situation: a site with *no*
    API, where BeautifulSoup has to parse HTML instead of `.json()`
    parsing a response body
"""

from __future__ import annotations

from typing import Any

import requests

from config import USER_AGENT

# PokeAPI resources are addressed like
# https://pokeapi.co/api/v2/pokemon/pikachu (name) or .../pokemon/25 (id) -
# REST's "everything is a URL" idea in its simplest form.
POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"


def get_pokemon(name_or_id: str | int) -> dict[str, Any]:
    """Fetch a single Pokemon resource from PokeAPI over plain HTTP.

    `name_or_id` can be the Pokemon's lowercase name ("pikachu") or its
    national Pokedex number (25) - PokeAPI accepts either as the final
    path segment.

    Raises requests.HTTPError if the Pokemon doesn't exist (PokeAPI
    returns 404) or the request otherwise fails. Returning None/partial
    data instead would let a caller silently work with a missing result;
    better to fail loudly at the point where the problem actually is.
    """
    url = f"{POKEAPI_BASE_URL}/pokemon/{name_or_id}"
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        # A timeout is not optional: without one, a hung connection would
        # block this script forever instead of raising an error.
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def summarize(pokemon: dict[str, Any]) -> dict[str, Any]:
    """Pull out the handful of fields this stage compares across sources.

    main.py calls this (or an equivalent) on data from every source -
    raw REST, requests-cache, pokebase, and the pokemondb.net scrape - so
    the same shape can be printed side by side regardless of where the
    data came from.
    """
    return {
        "id": pokemon["id"],
        "name": pokemon["name"],
        # PokeAPI reports height in decimetres and weight in hectograms -
        # an easy detail to miss, and worth comparing against
        # pokemondb_scraper.py's metres/kilograms later.
        "height_dm": pokemon["height"],
        "weight_hg": pokemon["weight"],
        "types": [entry["type"]["name"] for entry in pokemon["types"]],
        "abilities": [entry["ability"]["name"] for entry in pokemon["abilities"]],
        "sprite_url": pokemon["sprites"]["front_default"],
    }


if __name__ == "__main__":
    pikachu = get_pokemon("pikachu")
    for key, value in summarize(pikachu).items():
        print(f"{key}: {value}")
