# pokemon_scrapy

A [Scrapy](https://scrapy.org) project - scaffolded with
`scrapy startproject pokemon_scrapy` - that scrapes the same
[pokemondb.net](https://pokemondb.net) pages `../pokemondb_scraper.py`
does by hand, but using Scrapy's own architecture: a **spider** that
crawls from a list page to individual detail pages, and an **item
pipeline** that processes what the spider yields.

## The idea

`pokemondb_scraper.py` is a script: given one Pokemon's name, it fetches
one page, parses it, and downloads one image - it has no notion of "here
is a list of pages to visit." Scrapy's job is exactly that: crawling.

- **`pokemon_scrapy/spiders/pokemondb_spider.py`** - `PokemonDbSpider`
  starts at pokemondb.net's national pokedex list page, follows the link
  for each Pokemon (`response.follow(...)`, capped by a `-a limit=N`
  spider argument), and parses each one's page into a `PokemonItem` -
  the same fields `pokemondb_scraper.parse_pokemon_page()` extracts with
  BeautifulSoup, extracted here with Scrapy's own CSS/XPath selectors.
- **`pokemon_scrapy/items.py`** - `PokemonItem`, a dataclass describing
  the shape of what the spider yields (including `image_urls`, the field
  name Scrapy's image pipeline looks for by convention).
- **`pokemon_scrapy/pipelines.py`** - `DropIncompletePokemonPipeline`:
  drops (via `DropItem`) any item missing a required field, before it
  reaches anything downstream. This is what makes it "a pipeline" and
  not just "a spider that also validates inline" - the validation logic
  lives in its own class, wired up (along with Scrapy's own
  `ImagesPipeline`) through `ITEM_PIPELINES` in `settings.py`, not called
  directly from the spider.
- **`pokemon_scrapy/settings.py`** - where this project's politeness and
  behavior actually live: `ROBOTSTXT_OBEY = True` (Scrapy checks
  robots.txt itself before crawling a URL), `DOWNLOAD_DELAY = 2` +
  `CONCURRENT_REQUESTS_PER_DOMAIN = 1` (pokemondb.net's requested
  2-second crawl-delay, enforced project-wide instead of a manual
  `time.sleep()` call), `HTTPCACHE_ENABLED = True` (Scrapy's own
  response cache - the equivalent of `requests_cache.CachedSession` in
  `../cached_requests_demo.py`), and `IMAGES_STORE`/`ITEM_PIPELINES` for
  downloading artwork.

## Comparing this to `pokemondb_scraper.py`

| | `pokemondb_scraper.py` | `pokemon_scrapy/` |
|---|---|---|
| Crawling multiple pages | not built in - the caller loops over names itself (see `main.py`) | built in - the spider follows links itself, starting from one list page |
| Politeness (robots.txt, crawl-delay) | hand-written in `_get()` | project-wide settings (`ROBOTSTXT_OBEY`, `DOWNLOAD_DELAY`) |
| HTTP caching | `requests_cache.CachedSession` | `HTTPCACHE_ENABLED` |
| Parsing | BeautifulSoup (`soup.find(...)`) | Scrapy selectors (`response.css(...)`/`.xpath(...)`) |
| Downloading images | hand-written `download_artwork()` | `scrapy.pipelines.images.ImagesPipeline`, wired up in settings, not called directly |
| Output | Python dicts, for the caller to do whatever with | items exported via `-O file.json` (Scrapy's `FEEDS` mechanism) or printed to the console |

Neither is "better" - `pokemondb_scraper.py` is the better fit for
fetching one or a few known Pokemon on demand (which is all
`compile_pokedex.py` needs), the way `main.py` uses it. `pokemon_scrapy/`
is the better fit once the job is genuinely "crawl this site," since
Scrapy already handles concurrency, retries, and politeness
declaratively instead of needing them hand-built.

## Notes on ImagesPipeline

- `ImagesPipeline` saves each image under `images/full/<sha1-hash>.jpg`,
  named by a hash of its URL - not `<pokemon-name>.jpg` the way
  `pokemondb_scraper.download_artwork()` does. Match a downloaded image
  back to its Pokemon via the item's own `images` field (filled in by
  the pipeline with each image's `path`, `url`, and `checksum`), not the
  filename.
- Needs [Pillow](https://pillow.readthedocs.io/) installed - it's in the
  repo's `requirements.in`/`.txt` for exactly this reason. Without it,
  Scrapy disables `ImagesPipeline` with a warning at startup rather than
  failing the crawl.

## Running

From this folder (`data-scrape/pokemon_scrapy/`), with the repo's
`.venv` active:

```bash
scrapy crawl pokemondb -a limit=20 -O pokemon.json
```

- `-a limit=20` caps how many Pokemon get crawled (defaults to 20 if
  omitted). pokemondb.net's national list has ~1300 entries; at this
  project's 2-second `DOWNLOAD_DELAY`, crawling all of them takes
  40+ minutes - raise the limit deliberately, not by accident.
- `-O pokemon.json` exports every yielded item to that file (Scrapy's
  `FEEDS` mechanism, `-O` overwrites, `-o` appends). Omit it to just see
  items printed to the console.
- Downloaded artwork lands in `images/full/`; Scrapy's own HTTP cache in
  `.scrapy/httpcache/`. Neither is committed (see the root
  `.gitignore`) - both are reproducible by re-running the crawl.
