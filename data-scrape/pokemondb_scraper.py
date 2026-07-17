"""Concept: scraping HTML with BeautifulSoup, and downloading an image.

PokeAPI covers stats, types, and sprite URLs, but it has no page of
Pokemon-related trivia written as prose, and its sprites are small
in-game icons rather than official artwork. pokemondb.net
(https://pokemondb.net/pokedex/<name>) has both - the Pokemon's species
("Seed Pokemon"), height/weight in different units than PokeAPI uses, and
a larger official artwork image - but as an ordinary HTML page, not an
API. Getting that data means requesting the page like a browser would and
picking values out of the HTML with BeautifulSoup, instead of parsing
JSON.

Scraping etiquette this module follows:
  - pokemondb.net's robots.txt (https://pokemondb.net/robots.txt) allows
    crawling /pokedex/ pages for a generic user agent, but asks for a
    2-second `Crawl-delay` between requests - CRAWL_DELAY_SECONDS below.
  - Every request identifies this script with a descriptive User-Agent
    (see config.py) rather than spoofing a browser.
  - Requests go through requests-cache (like cached_requests_demo.py),
    both to avoid re-scraping the same page while iterating on this
    script, and so the crawl-delay sleep only happens on an actual
    network hit, never on a cache hit - a cache hit doesn't touch
    pokemondb.net at all, so the delay doesn't apply to it.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import requests_cache
from bs4 import BeautifulSoup, Tag

from config import USER_AGENT

STAGE_DIR = Path(__file__).parent
POKEMONDB_BASE_URL = "https://pokemondb.net"
IMAGES_DIR = STAGE_DIR / "images"

# Per pokemondb.net/robots.txt's `Crawl-delay: 2` for generic user agents.
CRAWL_DELAY_SECONDS = 2

session = requests_cache.CachedSession(
    str(STAGE_DIR / "pokemondb_cache"),
    backend="sqlite",
    # A page's content for a given Pokemon effectively never changes, so
    # a long expiry is fine - this cache exists to avoid hammering the
    # site while developing/re-running this script, not to serve
    # fast-changing data.
    expire_after=60 * 60 * 24 * 7,
)


def _get(url: str) -> requests_cache.CachedResponse:
    """GET a URL through the shared cached session, honoring crawl-delay.

    Every caller in this module (page fetch, image fetch) goes through
    this one function, so the crawl-delay logic only has to live here.
    """
    response = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    response.raise_for_status()
    if not response.from_cache:
        time.sleep(CRAWL_DELAY_SECONDS)
    return response


def _find_row_value(vitals_table: Tag, label_prefix: str) -> Tag | None:
    """Return the <td> for the <tr> whose <th> starts with `label_prefix`.

    pokemondb's "Pokedex data" table is a <th>label</th><td>value</td>
    pair per row (see the docstring in scrape_pokemon() for the row
    labels). Matching on a lowercase prefix - rather than the exact
    label text - sidesteps the HTML entity pokemondb uses for "No." in
    two of the row labels ("National No.", "Local No."), which is easy
    to get wrong copying into source code but irrelevant to what this
    function actually needs to find.
    """
    for row in vitals_table.find_all("tr"):
        header_cell = row.find("th")
        if header_cell and header_cell.get_text(strip=True).lower().startswith(
            label_prefix
        ):
            return row.find("td")
    return None


def scrape_pokemon(name: str) -> dict[str, Any]:
    """Scrape one Pokemon's pokemondb.net page for data PokeAPI doesn't have.

    Returns a dict with:
      - national_number (int)
      - species (str), e.g. "Seed Pokemon"
      - height_m (float | None), weight_kg (float | None) - note the
        different units from requests_basics.summarize()'s
        height_dm/weight_hg
      - types (list[str]), abilities (list[str]), hidden_ability (str | None)
      - artwork_url (str) - the official artwork image, for
        download_artwork() below

    Raises requests.HTTPError if the page doesn't exist (404, e.g. a
    misspelled name), same failure behavior as requests_basics.get_pokemon().
    """
    url = f"{POKEMONDB_BASE_URL}/pokedex/{name}"
    response = _get(url)
    return parse_pokemon_page(response.text)


def parse_pokemon_page(html: str) -> dict[str, Any]:
    """Pull the fields scrape_pokemon() needs out of a pokedex page's HTML.

    Split out from scrape_pokemon() so the parsing logic - the actual
    BeautifulSoup part of this module - can be unit-tested against a
    saved HTML fixture (see tests/test_pokemondb_scraper.py) without
    needing a live network call for every test run.
    """
    soup = BeautifulSoup(html, "html.parser")

    # The page has several class="vitals-table" tables (Pokedex data,
    # Training, Breeding, ...); the first one is "Pokedex data", which
    # has the fields this stage wants.
    vitals_table = soup.find("table", class_="vitals-table")

    national_number_cell = _find_row_value(vitals_table, "national")
    national_number = int(national_number_cell.get_text(strip=True))

    species = _find_row_value(vitals_table, "species").get_text(strip=True)

    # Height/weight cells look like "0.7\xa0m (2′04″)" and
    # "6.9\xa0kg (15.2\xa0lbs)" - the metric figure is the first token
    # before the unit, so split on the non-breaking space pokemondb uses.
    height_text = _find_row_value(vitals_table, "height").get_text(strip=True)
    height_m = float(height_text.split("\xa0m")[0])
    weight_text = _find_row_value(vitals_table, "weight").get_text(strip=True)
    weight_kg = float(weight_text.split("\xa0kg")[0])

    type_cell = _find_row_value(vitals_table, "type")
    types = [link.get_text(strip=True) for link in type_cell.find_all("a")]

    abilities_cell = _find_row_value(vitals_table, "abilities")
    abilities = [link.get_text(strip=True) for link in abilities_cell.find_all("a")]
    # pokemondb lists the hidden ability last and marks it with the text
    # "(hidden ability)" next to it, rather than a class/attribute on the
    # element - so detecting it means checking the cell's full text.
    hidden_ability = (
        abilities[-1] if "(hidden ability)" in abilities_cell.get_text() else None
    )

    # The official artwork <img> is inside a <picture> whose src always
    # points at img.pokemondb.net/artwork/<name>.jpg.
    artwork_img = soup.find("img", src=lambda src: src and "/artwork/" in src)
    artwork_url = artwork_img["src"]

    return {
        "national_number": national_number,
        "species": species,
        "height_m": height_m,
        "weight_kg": weight_kg,
        "types": types,
        "abilities": abilities,
        "hidden_ability": hidden_ability,
        "artwork_url": artwork_url,
    }


def download_artwork(name: str, artwork_url: str) -> Path:
    """Download a Pokemon's official artwork into IMAGES_DIR, if not already there.

    Returns the path the image was (or already had been) saved to.
    Skipping an existing file means re-running main.py doesn't re-fetch
    - or re-cache - images it already has.
    """
    IMAGES_DIR.mkdir(exist_ok=True)
    suffix = Path(artwork_url).suffix or ".jpg"
    dest_path = IMAGES_DIR / f"{name}{suffix}"

    if not dest_path.exists():
        response = _get(artwork_url)
        dest_path.write_bytes(response.content)

    return dest_path


if __name__ == "__main__":
    data = scrape_pokemon("bulbasaur")
    for key, value in data.items():
        print(f"{key}: {value}")
    saved_to = download_artwork("bulbasaur", data["artwork_url"])
    print(f"artwork saved to: {saved_to}")
