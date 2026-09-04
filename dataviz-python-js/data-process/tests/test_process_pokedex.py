"""Tests for process_pokedex's cleaning logic.

Uses synthetic rows shaped like data-scrape/pokedex.csv, rather than the
real CSV or a live network call, so these stay fast and independent of
how far data-scrape/compile_pokedex.py has progressed. `clean_row()`'s
`scrape_dir` argument points at a pytest `tmp_path` with a fake artwork
file, since `clean_row()` checks that file actually exists on disk.
"""

from pathlib import Path

from process_pokedex import clean_row, humanize

# A normal row, as PokeAPI + pokemondb.net would both succeed for it -
# every raw CSV value is a string, matching what csv.DictReader hands back.
BULBASAUR_ROW = {
    "national_number": "1",
    "name": "bulbasaur",
    "generation": "1",
    "species": "Seed Pokémon",
    "types": "grass;poison",
    "abilities": "overgrow;chlorophyll",
    "hidden_ability": "Chlorophyll",
    "height_dm": "7",
    "weight_hg": "69",
    "height_m": "0.7",
    "weight_kg": "6.9",
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
    "artwork_url": "https://img.pokemondb.net/artwork/bulbasaur.jpg",
    "artwork_path": "images/bulbasaur.jpg",
    "fetch_issues": "",
}

# Shaped like the real gengar/starly rows in pokedex.csv: PokeAPI failed,
# so height_dm/weight_hg/sprite_url are blank and types/abilities came
# from pokemondb.net's already-Title-Case text instead of PokeAPI's
# lowercase-hyphenated slugs.
GENGAR_ROW = {
    "national_number": "94",
    "name": "gengar",
    "generation": "1",
    "species": "Shadow Pokémon",
    "types": "Ghost;Poison",
    "abilities": "Cursed Body",
    "hidden_ability": "",
    "height_dm": "",
    "weight_hg": "",
    "height_m": "1.5",
    "weight_kg": "40.5",
    "sprite_url": "",
    "artwork_url": "https://img.pokemondb.net/artwork/gengar.jpg",
    "artwork_path": "images/gengar.jpg",
    "fetch_issues": "pokeapi: connection error",
}


def _make_scrape_dir(tmp_path: Path, artwork_path: str) -> Path:
    """A fake data-scrape/ directory with one real (empty) artwork file,
    so clean_row()'s "does the image exist on disk" check passes."""
    scrape_dir = tmp_path / "data-scrape"
    image_file = scrape_dir / artwork_path
    image_file.parent.mkdir(parents=True)
    image_file.write_bytes(b"")
    return scrape_dir


def test_humanize_normalizes_pokeapi_slugs_and_pokemondb_text_the_same_way() -> None:
    assert humanize("solar-power") == "Solar Power"
    assert humanize("Cursed Body") == "Cursed Body"


def test_clean_row_normal_case(tmp_path: Path) -> None:
    scrape_dir = _make_scrape_dir(tmp_path, "images/bulbasaur.jpg")
    cleaned = clean_row(BULBASAUR_ROW, scrape_dir)

    assert cleaned is not None
    assert cleaned["national_number"] == 1
    assert cleaned["display_name"] == "Bulbasaur"
    assert cleaned["types"] == ["Grass", "Poison"]
    assert cleaned["abilities"] == ["Overgrow", "Chlorophyll"]
    assert cleaned["hidden_ability"] == "Chlorophyll"
    assert cleaned["height_m"] == 0.7
    assert cleaned["weight_kg"] == 6.9
    assert cleaned["artwork"] == "images/bulbasaur.jpg"


def test_clean_row_backfills_missing_pokeapi_fields(tmp_path: Path) -> None:
    """The gengar/starly case: PokeAPI failed, so height_dm/weight_hg/
    sprite_url are blank - clean_row() should derive height_m/weight_kg
    are already present from pokemondb.net directly, and fall back to
    PokeAPI's own sprite URL pattern using the national number."""
    scrape_dir = _make_scrape_dir(tmp_path, "images/gengar.jpg")
    cleaned = clean_row(GENGAR_ROW, scrape_dir)

    assert cleaned is not None
    assert cleaned["height_m"] == 1.5
    assert cleaned["weight_kg"] == 40.5
    assert cleaned["sprite_url"] == (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/94.png"
    )
    # types/abilities came from pokemondb.net's Title-Case text here, not
    # PokeAPI's lowercase slugs - still normalized to the same shape.
    assert cleaned["types"] == ["Ghost", "Poison"]
    assert cleaned["abilities"] == ["Cursed Body"]


def test_clean_row_skips_when_artwork_file_is_missing(tmp_path: Path) -> None:
    # No file created at tmp_path/data-scrape/images/bulbasaur.jpg this time.
    scrape_dir = tmp_path / "data-scrape"
    scrape_dir.mkdir()
    assert clean_row(BULBASAUR_ROW, scrape_dir) is None


def test_clean_row_skips_when_species_is_blank(tmp_path: Path) -> None:
    scrape_dir = _make_scrape_dir(tmp_path, "images/bulbasaur.jpg")
    row = {**BULBASAUR_ROW, "species": ""}
    assert clean_row(row, scrape_dir) is None
