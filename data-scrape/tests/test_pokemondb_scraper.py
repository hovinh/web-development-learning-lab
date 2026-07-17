"""Tests for pokemondb_scraper's HTML parsing.

Parses a saved fixture page (tests/fixtures/bulbasaur.html) instead of
hitting pokemondb.net over the network - per docs/python-implementation.md,
tests in this repo target the mechanic worth verifying (here, the
BeautifulSoup parsing logic), not blanket coverage, and a parsing test
shouldn't depend on - or slow down for - a live network call.
"""

from pathlib import Path

import pytest

from pokemondb_scraper import parse_pokemon_page

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "bulbasaur.html"


@pytest.fixture
def bulbasaur_data() -> dict:
    html = FIXTURE_PATH.read_text(encoding="utf-8")
    return parse_pokemon_page(html)


def test_national_number(bulbasaur_data: dict) -> None:
    assert bulbasaur_data["national_number"] == 1


def test_species(bulbasaur_data: dict) -> None:
    assert bulbasaur_data["species"] == "Seed Pokémon"


def test_height_and_weight_are_parsed_as_metric_floats(bulbasaur_data: dict) -> None:
    # The fixture's raw text is "0.7\xa0m (2'04\")" / "6.9\xa0kg (15.2\xa0lbs)" -
    # this checks the metric figure is pulled out as a float, not left as
    # that raw, unit-suffixed string.
    assert bulbasaur_data["height_m"] == 0.7
    assert bulbasaur_data["weight_kg"] == 6.9


def test_types(bulbasaur_data: dict) -> None:
    assert bulbasaur_data["types"] == ["Grass", "Poison"]


def test_abilities_and_hidden_ability(bulbasaur_data: dict) -> None:
    assert bulbasaur_data["abilities"] == ["Overgrow", "Chlorophyll"]
    # Chlorophyll is listed with "(hidden ability)" in the fixture;
    # Overgrow is not - this is the case parse_pokemon_page() has to
    # detect from the cell's text rather than an HTML attribute.
    assert bulbasaur_data["hidden_ability"] == "Chlorophyll"


def test_artwork_url(bulbasaur_data: dict) -> None:
    assert bulbasaur_data["artwork_url"] == "https://img.pokemondb.net/artwork/bulbasaur.jpg"
