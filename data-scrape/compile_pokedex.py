"""Compile every Generation 1-6 Pokemon into one CSV, combining this
stage's earlier building blocks:

  - requests_basics.py (PokeAPI, REST) for stats-adjacent fields
  - pokemondb_scraper.py (BeautifulSoup scrape) for species/real-world
    height-weight, and each Pokemon's official artwork - downloaded into
    data-scrape/images/ the same way main.py's demo does

"Generations 1-6" here means the 721 *base species* PokeAPI lists under
generations I-VI (confirmed via GET .../generation/{1..6} - 151+100+135+
107+156+72 = 721), not the 800-row count in data-read-write/pokemon.csv.
That other dataset's 800 rows include alternate forms (Mega Evolutions,
etc.) as separate rows; those don't have a name/slug that lines up
cleanly across PokeAPI, pokebase, and pokemondb.net (pokemondb.net in
particular gives Mega forms no page of their own - they're a section
partway down their base species' page), so mapping them consistently
across three sources was out of scope for this exercise. Every base
species is included, hidden/Mega forms are not.

This is a long-running script: pokemondb.net's requested 2-second
crawl-delay (see pokemondb_scraper.py) applies to every page AND every
artwork image that isn't already cached/downloaded, so a full first run
over 721 species takes on the order of 45-60 minutes. Progress is
written to pokedex.csv incrementally (one row per species, flushed
immediately) specifically so this is safe to interrupt (Ctrl+C) and
resume later - re-running the script skips any species already present
in the CSV.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Any

import requests

import pokemondb_scraper
import requests_basics
from cached_requests_demo import session as pokeapi_session
from config import USER_AGENT

STAGE_DIR = Path(__file__).parent
CSV_PATH = STAGE_DIR / "pokedex.csv"

GENERATIONS = range(1, 7)  # Generations I-VI - this stage's chosen scope

# PokeAPI has no published rate limit for this scale of use, but a small
# delay between the ~721+ calls this script makes is a cheap way to
# avoid hammering it in a tight loop - unlike pokemondb.net, there's no
# robots.txt Crawl-delay requiring this, it's just good manners.
POKEAPI_REQUEST_DELAY_SECONDS = 0.25

CSV_FIELDNAMES = [
    "national_number",
    "name",
    "generation",
    "species",
    "types",
    "abilities",
    "hidden_ability",
    "height_dm",  # PokeAPI, decimetres
    "weight_hg",  # PokeAPI, hectograms
    "height_m",  # pokemondb.net, metres
    "weight_kg",  # pokemondb.net, kilograms
    "sprite_url",
    "artwork_url",
    "artwork_path",  # relative to this stage's folder, e.g. "images/bulbasaur.jpg"
    "fetch_issues",  # non-empty if a source failed for this row - see fetch_pokemon_row()
]


def build_species_list() -> list[tuple[int, str, int]]:
    """Return every (national_number, name, generation) for Generations I-VI.

    PokeAPI's /generation/{n} endpoint lists each generation's species
    with a `url` ending in its national number
    (".../pokemon-species/25/" -> 25), which is how national_number is
    recovered here without a separate lookup per species.
    """
    species: list[tuple[int, str, int]] = []
    for generation in GENERATIONS:
        url = f"{requests_basics.POKEAPI_BASE_URL}/generation/{generation}"
        response = pokeapi_session.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()
        for entry in response.json()["pokemon_species"]:
            national_number = int(entry["url"].rstrip("/").rsplit("/", 1)[-1])
            species.append((national_number, entry["name"], generation))
    species.sort(key=lambda row: row[0])
    return species


def resolve_default_variety_name(species_name: str) -> str:
    """Look up which `pokemon` resource is a species' default variety.

    Almost every species name doubles as PokeAPI's `pokemon` resource
    name directly (e.g. "bulbasaur"). A handful of species with multiple
    forms - e.g. "deoxys", whose forms are "deoxys-normal"/"-attack"/
    "-defense"/"-speed" - have no plain `pokemon` resource under the
    species name itself; PokeAPI marks one form `is_default` instead.
    Only called as a fallback after the direct name lookup 404s, since
    it costs an extra request and only a small minority of species need it.
    """
    url = f"{requests_basics.POKEAPI_BASE_URL}/pokemon-species/{species_name}"
    response = pokeapi_session.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
    response.raise_for_status()
    for variety in response.json()["varieties"]:
        if variety["is_default"]:
            return variety["pokemon"]["name"]
    raise ValueError(f"no default variety listed for species {species_name!r}")


def fetch_pokemon_row(national_number: int, name: str, generation: int) -> dict[str, Any]:
    """Combine PokeAPI + pokemondb.net data for one species into one CSV row.

    Each source is fetched in its own try/except: a failure in one
    (e.g. pokemondb.net 404s on a name PokeAPI accepted, or vice versa)
    still lets the other source's fields populate the row, rather than
    losing the whole row. `fetch_issues` records what went wrong so nulls
    in the final CSV are traceable back to a cause instead of looking
    like missing data for no reason.
    """
    row: dict[str, Any] = {field: "" for field in CSV_FIELDNAMES}
    row["national_number"] = national_number
    row["name"] = name
    row["generation"] = generation
    issues: list[str] = []

    try:
        time.sleep(POKEAPI_REQUEST_DELAY_SECONDS)
        pokeapi_url = f"{requests_basics.POKEAPI_BASE_URL}/pokemon/{name}"
        response = pokeapi_session.get(pokeapi_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if response.status_code == 404:
            resolved_name = resolve_default_variety_name(name)
            time.sleep(POKEAPI_REQUEST_DELAY_SECONDS)
            pokeapi_url = f"{requests_basics.POKEAPI_BASE_URL}/pokemon/{resolved_name}"
            response = pokeapi_session.get(pokeapi_url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()

        summary = requests_basics.summarize(response.json())
        row["types"] = ";".join(summary["types"])
        row["abilities"] = ";".join(summary["abilities"])
        row["height_dm"] = summary["height_dm"]
        row["weight_hg"] = summary["weight_hg"]
        row["sprite_url"] = summary["sprite_url"] or ""
    except requests.RequestException as error:
        issues.append(f"pokeapi: {error}")

    try:
        scraped = pokemondb_scraper.scrape_pokemon(name)
        row["species"] = scraped["species"]
        row["height_m"] = scraped["height_m"]
        row["weight_kg"] = scraped["weight_kg"]
        row["hidden_ability"] = scraped["hidden_ability"] or ""
        row["artwork_url"] = scraped["artwork_url"]
        # Only fall back to pokemondb's types/abilities if PokeAPI's own
        # lookup above failed - PokeAPI is the primary source for these
        # two fields (see requests_basics.summarize()), pokemondb.net is
        # the backup, not the other way around.
        if not row["types"]:
            row["types"] = ";".join(scraped["types"])
        if not row["abilities"]:
            row["abilities"] = ";".join(scraped["abilities"])

        artwork_path = pokemondb_scraper.download_artwork(name, scraped["artwork_url"])
        # .as_posix() (forward slashes) rather than str() (whatever the
        # OS uses) - so the CSV's paths look the same whether it's
        # produced on Windows or opened later on Linux/macOS.
        row["artwork_path"] = artwork_path.relative_to(STAGE_DIR).as_posix()
    except requests.RequestException as error:
        issues.append(f"pokemondb: {error}")

    row["fetch_issues"] = "; ".join(issues)
    return row


def already_compiled_names(csv_path: Path) -> set[str]:
    """Names already written to a previous run's CSV, so compile_pokedex()
    can skip them and resume an interrupted run instead of starting over."""
    if not csv_path.exists():
        return set()
    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        return {row["name"] for row in csv.DictReader(csv_file)}


def compile_pokedex(limit: int | None = None) -> None:
    species_list = build_species_list()
    if limit is not None:
        species_list = species_list[:limit]

    done = already_compiled_names(CSV_PATH)
    write_header = not CSV_PATH.exists()
    print(
        f"{len(species_list)} species targeted; "
        f"{len(done)} already in {CSV_PATH.name} from a previous run"
    )

    # Append mode + a flush() after every row: if this script is
    # interrupted partway through, everything written so far stays on
    # disk, and already_compiled_names() picks up from there next time.
    with CSV_PATH.open("a", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        if write_header:
            writer.writeheader()

        for index, (national_number, name, generation) in enumerate(species_list, start=1):
            if name in done:
                continue

            print(f"[{index}/{len(species_list)}] #{national_number:04d} {name}")
            row = fetch_pokemon_row(national_number, name, generation)
            writer.writerow(row)
            csv_file.flush()

            if row["fetch_issues"]:
                print(f"    issues: {row['fetch_issues']}", file=sys.stderr)

    print(f"Done. Compiled data is in {CSV_PATH}, artwork in {STAGE_DIR / 'images'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile Generation 1-6 Pokemon data + artwork into one CSV."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N species (national dex order) - useful for a quick trial run.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    compile_pokedex(limit=args.limit)
