# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field


@dataclass
class PokemonItem:
    """One Pokemon scraped from a pokemondb.net pokedex page.

    Mirrors the fields pokemondb_scraper.parse_pokemon_page() (one
    directory up) extracts by hand with BeautifulSoup - same data, same
    site, different framework. The two are worth comparing side by side.
    """

    name: str = ""
    national_number: int = 0
    species: str = ""
    height_m: float = 0.0
    weight_kg: float = 0.0
    types: list = field(default_factory=list)
    abilities: list = field(default_factory=list)
    hidden_ability: str | None = None

    # `image_urls` is the field name scrapy.pipelines.images.ImagesPipeline
    # looks for by convention; it fills in `images` itself (with the
    # downloaded file's local path, checksum, etc.) after downloading -
    # this project's code never writes to `images` directly. See
    # ITEM_PIPELINES in settings.py.
    image_urls: list = field(default_factory=list)
    images: list = field(default_factory=list)
