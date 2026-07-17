"""Concept: caching HTTP requests with requests-cache.

Calling the same PokeAPI URL over and over - e.g. while iterating on a
script, or re-running it during development - is wasted network traffic:
the data for "pikachu" isn't going to change between two runs a minute
apart. `requests_cache.CachedSession` is a near drop-in replacement for
`requests.Session` that transparently stores each response (here, in a
local SQLite file) and replays it instead of hitting the network again,
as long as the cached entry hasn't expired.

Compare this file to requests_basics.py: the only real difference is
`requests.get(...)` becoming `session.get(...)` on a CachedSession -
everything else about calling the REST API is identical.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests_cache

from config import USER_AGENT
from requests_basics import POKEAPI_BASE_URL, summarize

STAGE_DIR = Path(__file__).parent

# A SQLite file next to this script, rather than an in-memory cache, so
# entries also survive between separate runs of this script - not just
# within one process's lifetime.
CACHE_PATH = str(STAGE_DIR / "http_cache")

# PokeAPI's data for a given Pokemon essentially never changes, so a long
# expiry is safe here; a news API or a stock-price API would need a much
# shorter one (seconds to minutes) to avoid serving stale data.
session = requests_cache.CachedSession(
    CACHE_PATH, backend="sqlite", expire_after=60 * 60 * 24
)


def get_pokemon_cached(name_or_id: str | int) -> requests_cache.CachedResponse:
    """Same request as requests_basics.get_pokemon(), through the cache."""
    url = f"{POKEAPI_BASE_URL}/pokemon/{name_or_id}"
    response = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    response.raise_for_status()
    return response


def summarize_cached(pokemon: dict[str, Any]) -> dict[str, Any]:
    """Alias so callers don't need to import requests_basics separately."""
    return summarize(pokemon)


if __name__ == "__main__":
    # Clear any cache left over from a previous run, so this demo always
    # shows a real cache MISS on the first call below.
    session.cache.clear()

    for label in ("first call (expect a MISS)", "second call (expect a HIT)"):
        start = time.perf_counter()
        response = get_pokemon_cached("pikachu")
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"{label}: from_cache={response.from_cache}, {elapsed_ms:.1f} ms")

    print(summarize_cached(response.json()))
