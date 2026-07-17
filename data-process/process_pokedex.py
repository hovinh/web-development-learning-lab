"""Clean up data-scrape/pokedex.csv into one standardized dataset for a web page.

data-scrape/compile_pokedex.py merges two sources (PokeAPI + a
pokemondb.net scrape) per row, and by design lets either source fail
independently without dropping the row (see that stage's README). That's
the right call for *collecting* the data, but it leaves the raw CSV with
exactly the kind of inconsistencies a web page shouldn't have to work
around:

  - **Mixed casing**: types/abilities normally come from PokeAPI as
    lowercase, hyphenated slugs ("solar-power"), but fall back to
    pokemondb.net's already-human-readable text ("Cursed Body") on the
    rows where PokeAPI's own request failed. Same underlying data, two
    different formats depending on which source happened to answer.
  - **Missing fields with a derivable substitute**: those same rows are
    missing PokeAPI's height_dm/weight_hg/sprite_url - but height_m/
    weight_kg (from pokemondb.net) are just a unit conversion away, and
    a sprite URL follows a predictable pattern from the national number.
  - **Two unit systems**: the raw CSV keeps both PokeAPI's decimetres/
    hectograms and pokemondb.net's metres/kilograms side by side (a
    deliberate comparison point in that stage - see its README). A web
    page needs to pick exactly one to display; this script standardizes
    on metric metres/kilograms.
  - **Inconsistent image sizes**: pokemondb.net's official artwork is a
    different width x height per Pokemon (whatever its natural artwork
    shape is - see this stage's README for a size sample). A web page
    laying these out in a grid wants one consistent size.

This script fixes all four, producing:
  - `pokedex.json` - one JSON array, sorted by national number, with
    consistent field casing/units and no source-dependent gaps.
  - `images/<name>.jpg` - every artwork image resized/padded onto a
    fixed-size white square (THUMBNAIL_SIZE below).

It's safe to run against a still-in-progress data-scrape/pokedex.csv
(data-scrape/compile_pokedex.py takes 45-60 minutes for the full
Pokedex) - just re-run this script after that one finishes to pick up
the rest.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

STAGE_DIR = Path(__file__).parent
SCRAPE_DIR = STAGE_DIR.parent / "data-scrape"
CSV_PATH = SCRAPE_DIR / "pokedex.csv"

OUTPUT_JSON_PATH = STAGE_DIR / "pokedex.json"
OUTPUT_IMAGES_DIR = STAGE_DIR / "images"

# The fixed square every artwork image gets resized/padded to fit. 300x300
# is an arbitrary but reasonable thumbnail size for a card-grid web page;
# change it here if a future web page stage needs a different size.
THUMBNAIL_SIZE = (300, 300)


def humanize(slug_or_text: str) -> str:
    """Normalize a type/ability string to one consistent "Title Case" form,
    regardless of whether it arrived as a PokeAPI slug ("solar-power") or
    already-human-readable pokemondb.net text ("Cursed Body").

    `.title()` is idempotent on text that's already Title Case, so this
    is safe to apply to every row without knowing in advance which
    source it actually came from.
    """
    return slug_or_text.replace("-", " ").replace("_", " ").title()


def _parse_float(value: str) -> float | None:
    value = value.strip()
    return float(value) if value else None


def clean_row(raw: dict[str, str], scrape_dir: Path) -> dict[str, Any] | None:
    """Turn one raw pokedex.csv row into one standardized dict, or None
    if the row isn't usable web material (no artwork, or both sources
    failed for a field with no fallback).

    Returning None (rather than raising) is deliberate: one bad row
    shouldn't stop the whole dataset from being produced - see
    process_pokedex()'s `skipped` list for what got dropped and why.
    """
    name = raw["name"].strip()
    species = raw["species"].strip()
    if not name or not species:
        return None

    artwork_path = raw["artwork_path"].strip()
    if not artwork_path or not (scrape_dir / artwork_path).is_file():
        # No image on disk means nothing to show on a web page, no
        # matter how complete the rest of the row is.
        return None

    height_m = _parse_float(raw["height_m"])
    if height_m is None and raw["height_dm"].strip():
        height_m = _parse_float(raw["height_dm"]) / 10  # decimetres -> metres
    weight_kg = _parse_float(raw["weight_kg"])
    if weight_kg is None and raw["weight_hg"].strip():
        weight_kg = _parse_float(raw["weight_hg"]) / 10  # hectograms -> kilograms
    if height_m is None or weight_kg is None:
        return None  # both sources failed for this field - nothing to derive from

    types = [humanize(entry) for entry in raw["types"].split(";") if entry]
    abilities = [humanize(entry) for entry in raw["abilities"].split(";") if entry]

    hidden_ability = humanize(raw["hidden_ability"]) if raw["hidden_ability"].strip() else None
    if hidden_ability and hidden_ability not in abilities:
        # Should never happen - the hidden ability is supposed to be one
        # of the Pokemon's own abilities - so this is worth surfacing
        # rather than silently keeping a value that contradicts `abilities`.
        print(
            f"  warning: {name}'s hidden ability {hidden_ability!r} "
            f"isn't in its abilities list {abilities}",
            file=sys.stderr,
        )

    sprite_url = raw["sprite_url"].strip()
    if not sprite_url:
        # PokeAPI's own sprite URLs all follow this pattern - falling
        # back to it directly avoids leaving the field blank on the
        # handful of rows where the PokeAPI request itself failed.
        sprite_url = (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master"
            f"/sprites/pokemon/{raw['national_number']}.png"
        )

    return {
        "national_number": int(raw["national_number"]),
        "name": name,
        "display_name": name.replace("-", " ").title(),
        "generation": int(raw["generation"]),
        "species": species,
        "types": types,
        "abilities": abilities,
        "hidden_ability": hidden_ability,
        "height_m": round(height_m, 2),
        "weight_kg": round(weight_kg, 2),
        "sprite_url": sprite_url,
        "artwork": f"images/{name}.jpg",
    }


def standardize_image(source_path: Path, dest_path: Path, size: tuple[int, int]) -> None:
    """Resize `source_path` to fit within `size` and pad it onto a white
    square of exactly `size`, saved to `dest_path`.

    Skips the work if `dest_path` already exists, same reasoning as
    data-scrape/pokemondb_scraper.py's download_artwork(): re-running
    this script shouldn't redo image processing it's already done.
    """
    if dest_path.exists():
        return

    with Image.open(source_path) as original:
        # .convert("RGB") drops any alpha channel before pasting onto an
        # opaque background - the source JPEGs have none, but this makes
        # the function safe if a future source ever provides PNGs with
        # transparency instead.
        resized = original.convert("RGB")
        # .thumbnail() resizes in place, preserving aspect ratio, so a
        # tall image and a wide image both end up no larger than `size`
        # in either dimension - never stretched or cropped.
        resized.thumbnail(size, Image.LANCZOS)

        canvas = Image.new("RGB", size, (255, 255, 255))
        offset = ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2)
        canvas.paste(resized, offset)
        canvas.save(dest_path, "JPEG", quality=90)


def process_pokedex() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} not found - run data-scrape/compile_pokedex.py first"
        )

    with CSV_PATH.open(encoding="utf-8", newline="") as csv_file:
        raw_rows = list(csv.DictReader(csv_file))

    OUTPUT_IMAGES_DIR.mkdir(exist_ok=True)

    cleaned_rows: list[dict[str, Any]] = []
    skipped_names: list[str] = []
    for raw in raw_rows:
        cleaned = clean_row(raw, SCRAPE_DIR)
        if cleaned is None:
            skipped_names.append(raw["name"])
            continue

        standardize_image(
            SCRAPE_DIR / raw["artwork_path"],
            OUTPUT_IMAGES_DIR / f"{cleaned['name']}.jpg",
            THUMBNAIL_SIZE,
        )
        cleaned_rows.append(cleaned)

    cleaned_rows.sort(key=lambda row: row["national_number"])

    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as json_file:
        # ensure_ascii=False keeps species text like "Seed Pokémon"
        # as real UTF-8 rather than a "\uXXXX" escape - a web page's
        # fetch()+JSON.parse() handles UTF-8 natively, no reason to hide it.
        json.dump(cleaned_rows, json_file, indent=2, ensure_ascii=False)

    print(f"Processed {len(cleaned_rows)} Pokemon into {OUTPUT_JSON_PATH.name}")
    if skipped_names:
        print(
            f"Skipped {len(skipped_names)} incomplete row(s): "
            f"{', '.join(skipped_names)}"
        )


if __name__ == "__main__":
    process_pokedex()
