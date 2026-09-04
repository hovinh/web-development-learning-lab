"""Scrapy version of pokemondb_scraper.py, one directory up.

Same site, same data, same underlying HTML - but Scrapy's shape instead
of a hand-rolled requests+BeautifulSoup script:

  - a Spider starts at one page (the national pokedex list) and follows
    links to others (each Pokemon's own page) - `scrapy_basics.py`'s
    equivalent, `pokemondb_scraper.py`, is only ever told one name at a
    time by its caller; it has no notion of "crawl" at all.
  - politeness (robots.txt, crawl-delay, caching) is *project-wide
    configuration* in settings.py, not code this spider has to write
    itself - contrast with pokemondb_scraper.py's `_get()` helper, which
    implements the delay and cache-check by hand.
  - the item this spider yields is handed off to a *separate* pipeline
    (pipelines.py's DropIncompletePokemonPipeline, then Scrapy's built-in
    ImagesPipeline) rather than the spider doing validation and
    downloading itself inline.

Run it (from this pokemon_scrapy/ folder, with the repo's venv active):

    scrapy crawl pokemondb -a limit=20 -O pokemon.json

`-a limit=20` caps how many Pokemon pages get crawled (defaults to 20)-
pokemondb.net's national list has ~1300 entries, and at this project's
2-second DOWNLOAD_DELAY (settings.py), crawling all of them takes
40+ minutes. `-O pokemon.json` exports every yielded item to that file
(Scrapy's FEEDS mechanism) - drop it to just see items printed to the
console instead.
"""

from __future__ import annotations

from typing import Any

import scrapy
from scrapy.http import Response

from pokemon_scrapy.items import PokemonItem


class PokemonDbSpider(scrapy.Spider):
    name = "pokemondb"
    allowed_domains = ["pokemondb.net"]
    start_urls = ["https://pokemondb.net/pokedex/national"]

    def __init__(self, limit: str = "20", *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Spider arguments (`-a name=value` on the command line) always
        # arrive as strings, hence the explicit int() conversion here.
        self.limit = int(limit)

    def parse(self, response: Response):
        """Parse the national pokedex list page: one link per Pokemon.

        Every Pokemon's name+link appears once on this page as an
        `<a class="ent-name" href="/pokedex/...">`. `response.follow()`
        turns that relative href into a full URL and schedules a new
        request for it - this is the "spider" part: one page's parse
        method discovering more pages to visit.
        """
        detail_links = response.css("a.ent-name::attr(href)").getall()
        for href in detail_links[: self.limit]:
            yield response.follow(href, callback=self.parse_pokemon)

    def parse_pokemon(self, response: Response):
        """Parse one Pokemon's own pokedex page into a PokemonItem.

        Mirrors pokemondb_scraper.parse_pokemon_page() field-for-field,
        but with Scrapy's built-in CSS/XPath selectors instead of
        BeautifulSoup - `response.css(...)`/`response.xpath(...)` walk
        the same parsed HTML tree BeautifulSoup would, just through a
        different API.
        """
        name = response.url.rstrip("/").rsplit("/", 1)[-1]

        # The page has several class="vitals-table" tables (Pokedex
        # data, Training, Breeding, ...); the first one is "Pokedex
        # data", which has the fields this spider wants - same as
        # pokemondb_scraper.py's `soup.find("table", class_="vitals-table")`.
        vitals_table = response.css("table.vitals-table")[0]

        national_number = int(
            self._row_value(vitals_table, "National").css("strong::text").get()
        )
        species = self._row_value(vitals_table, "Species").css("::text").get()

        # Height/weight cells look like "0.7\xa0m (2'04\")" and
        # "6.9\xa0kg (15.2\xa0lbs)" - same parsing as pokemondb_scraper.py.
        height_text = "".join(self._row_value(vitals_table, "Height").css("::text").getall())
        height_m = float(height_text.split("\xa0m")[0])
        weight_text = "".join(self._row_value(vitals_table, "Weight").css("::text").getall())
        weight_kg = float(weight_text.split("\xa0kg")[0])

        types = self._row_value(vitals_table, "Type").css("a::text").getall()

        abilities_cell = self._row_value(vitals_table, "Abilities")
        abilities = abilities_cell.css("a::text").getall()
        hidden_ability = None
        if "(hidden ability)" in "".join(abilities_cell.css("::text").getall()):
            hidden_ability = abilities[-1]

        artwork_url = response.css('img[src*="/artwork/"]::attr(src)').get()

        yield PokemonItem(
            name=name,
            national_number=national_number,
            species=species,
            height_m=height_m,
            weight_kg=weight_kg,
            types=types,
            abilities=abilities,
            hidden_ability=hidden_ability,
            image_urls=[artwork_url] if artwork_url else [],
        )

    @staticmethod
    def _row_value(vitals_table, label: str):
        """Return the <td> Selector for the <tr> whose <th> starts with `label`.

        The XPath equivalent of pokemondb_scraper.py's `_find_row_value()`
        helper - same reason for matching a prefix rather than exact
        text: two of pokemondb's row labels ("National No.", "Local
        No.") use an HTML entity for "No." that's easy to mistype in
        source code but irrelevant to what this needs to find.
        """
        return vitals_table.xpath(f'.//tr[th[starts-with(text(), "{label}")]]/td')[0]
