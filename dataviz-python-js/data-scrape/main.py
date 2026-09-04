"""Entry point/demo for the data-scrape stage.

Runs all four ways of getting Pokemon data covered by this stage, back to
back, for the same Pokemon where that's meaningful:

1. requests_basics     - raw `requests` call to PokeAPI's REST API
2. cached_requests_demo - the same call through requests-cache
3. pokebase_demo        - the same data via a dedicated client library
4. pokemondb_scraper    - BeautifulSoup scrape of a site with no API,
                          plus downloading each Pokemon's artwork image

See data-scrape/README.md for the reasoning behind each approach and
when you'd actually reach for it.
"""

from __future__ import annotations

import time

import cached_requests_demo
import pokebase_demo
import pokemondb_scraper
import requests_basics

POKEMON_TO_SCRAPE = ["bulbasaur", "charmander", "squirtle", "pikachu"]


def demo_rest_api() -> None:
    print("\n=== 1. requests_basics: raw REST call to PokeAPI ===")
    pikachu = requests_basics.get_pokemon("pikachu")
    for key, value in requests_basics.summarize(pikachu).items():
        print(f"  {key}: {value}")


def demo_cached_requests() -> None:
    print("\n=== 2. cached_requests_demo: the same call, cached ===")
    cached_requests_demo.session.cache.clear()
    for label in ("first call (MISS)", "second call (HIT)"):
        start = time.perf_counter()
        response = cached_requests_demo.get_pokemon_cached("pikachu")
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"  {label}: from_cache={response.from_cache}, {elapsed_ms:.1f} ms")


def demo_library_client() -> None:
    print("\n=== 3. pokebase_demo: same data via a client library ===")
    pikachu = pokebase_demo.get_pokemon_via_library("pikachu")
    for key, value in pokebase_demo.summarize_via_library(pikachu).items():
        print(f"  {key}: {value}")


def demo_scrape_and_download() -> None:
    print("\n=== 4. pokemondb_scraper: HTML scrape + artwork download ===")
    for name in POKEMON_TO_SCRAPE:
        data = pokemondb_scraper.scrape_pokemon(name)
        saved_to = pokemondb_scraper.download_artwork(name, data["artwork_url"])
        print(
            f"  {name}: species={data['species']!r}, "
            f"height_m={data['height_m']}, weight_kg={data['weight_kg']}, "
            f"types={data['types']}, artwork -> {saved_to}"
        )


if __name__ == "__main__":
    demo_rest_api()
    demo_cached_requests()
    demo_library_client()
    demo_scrape_and_download()
