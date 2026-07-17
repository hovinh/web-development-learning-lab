# data-scrape

Practice stage for getting Pokemon data off the internet: a raw
`requests` call to a RESTful API, the same call wrapped in
`requests-cache`, the same data again through a dedicated API client
library (`pokebase`), and - for data no API exposes - scraping an
ordinary HTML page with BeautifulSoup, including downloading an image.
`pokemon_scrapy/` repeats the BeautifulSoup exercise as a proper Scrapy
project (a spider + an item pipeline), and `compile_pokedex.py` uses the
earlier building blocks in bulk to compile every Generation 1-6 Pokemon
into one CSV with a folder of artwork.

## The idea

[PokeAPI](https://pokeapi.co) is a public, no-auth-required REST API:
every resource (a Pokemon, a type, an ability, ...) lives at its own URL,
and a GET request returns it as JSON. That makes it a clean way to
practice the basics of `requests` without a scraping stage's usual
complications (login walls, JavaScript-rendered content, messy markup).
This stage climbs through four layers on top of that starting point:

1. **`requests_basics.py`** - the "just `requests`" baseline. Build a
   URL, `requests.get()` it, call `.json()`, pull fields back out of the
   response dict by key. This is what "calling a RESTful Web API" means
   at its simplest.
2. **`cached_requests_demo.py`** - the same call through
   `requests_cache.CachedSession`, a near drop-in replacement for
   `requests.Session` that transparently stores responses (in a local
   SQLite file here) and replays them instead of re-hitting the network,
   as long as the entry hasn't expired. Re-running a script shouldn't
   have to re-fetch data that hasn't changed.
3. **`pokebase_demo.py`** - the same data again, through
   [`pokebase`](https://github.com/PokeAPI/pokebase), a small third-party
   client library built specifically for PokeAPI. It already knows the
   endpoint URLs and response shapes, so calling code works with
   attributes (`pokemon.types[0].type.name`) instead of raw dict/key
   lookups (`pokemon["types"][0]["type"]["name"]`) - the general
   trade-off of a "library API" wrapper around a REST API: less
   boilerplate, at the cost of a dependency that has to keep up with the
   underlying API.
4. **`pokemondb_scraper.py`** - PokeAPI has no page of Pokemon trivia
   written as prose, and its sprites are small in-game icons, not
   official artwork. [pokemondb.net](https://pokemondb.net) has both, but
   as an ordinary web page, not an API - so getting that data means
   requesting the page like a browser would and picking values out of
   the HTML with BeautifulSoup instead of parsing JSON. This module also
   downloads each Pokemon's official artwork image, the "scrape an
   image" exercise.

`main.py` runs all four, back to back, for the same Pokemon (Pikachu)
where that comparison is meaningful, then scrapes+downloads a small list
of Pokemon in the fourth step.

Two more pieces build on top of those four:

5. **`pokemon_scrapy/`** - the same pokemondb.net data as
   `pokemondb_scraper.py`, but as a real
   [Scrapy](https://scrapy.org) project instead of a hand-rolled script:
   a **spider** (`PokemonDbSpider`) that starts at the national pokedex
   list and follows links to each Pokemon's own page, and an **item
   pipeline** (`DropIncompletePokemonPipeline`) that validates each
   scraped item before Scrapy's built-in `ImagesPipeline` downloads its
   artwork. See `pokemon_scrapy/README.md`.
6. **`compile_pokedex.py`** - a bulk pipeline over the first four
   modules: fetches every Generation 1-6 Pokemon (721 species) from both
   PokeAPI and pokemondb.net and compiles the combined result into one
   CSV (`pokedex.csv`), downloading every artwork image into `images/`
   along the way.

## Choosing an approach

| | Raw `requests` (`requests_basics.py`) | `requests-cache` (`cached_requests_demo.py`) | `pokebase` (`pokebase_demo.py`) | BeautifulSoup (`pokemondb_scraper.py`) |
|---|---|---|---|---|
| Reach for it when... | the API is simple, called rarely, or you want to see exactly what's on the wire | you'll call the same endpoint repeatedly (development iteration, a script that re-runs on a schedule) and the data doesn't change every call | a well-maintained client library already exists for the API you're using, and its shape matches what you need | the data you need has no API at all |
| Cost | none beyond the API's own JSON shape - you own that shape in your code | one more dependency and a cache invalidation policy (`expire_after`) to pick | tied to however the library models the API - a mismatch between the library's version and the live API can silently produce stale or wrong shapes | most fragile: any redesign of the site's HTML breaks the scraper, and it's slower (network + a crawl-delay) than a JSON API |

The honest takeaway: prefer the API over scraping whenever one exists -
PokeAPI's stats/types/abilities are all handled better by
`requests_basics.py`/`pokebase_demo.py` than by scraping ever would be.
Scraping is what's left in `pokemondb_scraper.py` here for the data
PokeAPI genuinely doesn't have.

## Files

- `config.py` - the shared `USER_AGENT` string every request in this
  stage sends. See "Notes on scraping etiquette" below for why.
- `requests_basics.py` - `get_pokemon()`/`summarize()`: the plain
  `requests` call to PokeAPI and a dict of the fields this stage compares
  across sources.
- `cached_requests_demo.py` - `get_pokemon_cached()`: the same call
  through a `requests_cache.CachedSession`, printing `from_cache` and
  timing for a first (MISS) and second (HIT) call.
- `pokebase_demo.py` - `get_pokemon_via_library()`/
  `summarize_via_library()`: the same data via `pokebase`, in the same
  output shape as `requests_basics.summarize()` for side-by-side
  comparison.
- `pokemondb_scraper.py` - `scrape_pokemon()`: fetches a pokemondb.net
  pokedex page and parses it with BeautifulSoup (`parse_pokemon_page()`
  holds the actual parsing logic, split out so it's unit-testable
  against a saved fixture - see "Testing" below); `download_artwork()`:
  saves the page's official artwork image into `images/`.
- `main.py` - entry point/demo: runs all four approaches for Pikachu,
  then scrapes+downloads artwork for Bulbasaur, Charmander, Squirtle, and
  Pikachu.
- `tests/test_pokemondb_scraper.py`, `tests/fixtures/bulbasaur.html` -
  unit tests for the HTML parsing, against a saved (not live) page
  fixture.
- `conftest.py` - empty; its presence is what lets `tests/` import
  `pokemondb_scraper` without a package (see the file's own docstring).
- `pokemon_scrapy/` - a self-contained Scrapy project (its own
  `README.md` inside covers it in detail).
- `compile_pokedex.py` - bulk pipeline over `requests_basics.py` +
  `pokemondb_scraper.py`; see "Compiling the full dataset" below.
- `http_cache.sqlite`, `pokemondb_cache.sqlite`, `pokebase_cache/`,
  `images/`, `pokedex.csv` - all generated by running `main.py`/
  `compile_pokedex.py`; not committed (see root `.gitignore`) since
  they're fully reproducible.

## Notes on requests-cache

- `expire_after=60*60*24` (1 day) is used for both the PokeAPI cache
  (`cached_requests_demo.py`) and the pokemondb.net cache
  (`pokemondb_scraper.py`, 7 days there) because this stage's data
  essentially never changes between runs. A fast-moving API (stock
  prices, a live news feed) would need a much shorter expiry, or none at
  all for data that must always be fresh.
- `session.cache.clear()` in `cached_requests_demo.py`'s demo block
  exists purely so the printed output always shows a genuine MISS on the
  first call; a real script wouldn't normally clear its own cache on
  every run.

## Notes on pokebase

- pokebase caches every response to disk on its own, separately from
  requests-cache - by default under the user's home directory
  (`~/.cache/pokebase`, following the XDG Base Directory spec). This
  stage points that at `data-scrape/pokebase_cache/` instead
  (`pokebase.cache.set_cache(...)` in `pokebase_demo.py`), so the cache
  stays local to this repo. That call has to happen before any
  `pokebase.*` call is made, per pokebase's own documentation.
- pokebase's HTTP calls send no explicit User-Agent (`requests`' default,
  `python-requests/x.y`) - which PokeAPI accepts fine. This stage's own
  requests still set an explicit `USER_AGENT` (see below), since pokebase
  itself doesn't give a way to override its outgoing headers.

## Notes on scraping etiquette (`pokemondb_scraper.py`)

- Every request in this stage - PokeAPI and pokemondb.net alike - sends a
  descriptive `User-Agent` (`config.USER_AGENT`) instead of relying on a
  library's default or spoofing a browser. Two reasons: it's more honest
  (a server can usually tell a script is a script anyway), and it's
  occasionally necessary - PokeAPI's CDN returns `403 Forbidden` for
  Python's *bare* `urllib` default User-Agent, though it accepts
  `requests`' own default or this stage's explicit one just fine. Sites
  vary, so setting your own is the safer habit.
- [pokemondb.net's robots.txt](https://pokemondb.net/robots.txt) allows
  crawling `/pokedex/` pages for a generic user agent, but asks for a
  2-second `Crawl-delay` - `CRAWL_DELAY_SECONDS` in
  `pokemondb_scraper.py`. That sleep only happens after an actual network
  request, never after a cache hit, since a cache hit doesn't touch
  pokemondb.net at all.
- `download_artwork()` skips re-downloading a file that's already in
  `images/`, so re-running `main.py` doesn't re-fetch (or re-request
  through the cache) images it already has.

## Notes on the PokeAPI response shape

- PokeAPI reports height in **decimetres** and weight in
  **hectograms** (`requests_basics.summarize()`'s `height_dm`/
  `weight_hg`); pokemondb.net's page states height in **metres** and
  weight in **kilograms** (`pokemondb_scraper.scrape_pokemon()`'s
  `height_m`/`weight_kg`). Comparing the two sources for the same
  Pokemon in `main.py`'s output is a reminder that combining data from
  different APIs/sites means checking their units match before doing any
  math with them - they often don't.

## Notes on the Scrapy version (`pokemon_scrapy/`)

- Same data, same site, as `pokemondb_scraper.py` - but politeness
  (robots.txt, crawl-delay, caching) moves from code (`_get()`'s manual
  `time.sleep()` and `requests_cache.CachedSession`) to project-wide
  *settings* (`ROBOTSTXT_OBEY`, `DOWNLOAD_DELAY`, `HTTPCACHE_ENABLED`),
  and downloading artwork moves from a hand-written function
  (`download_artwork()`) to a built-in pipeline
  (`scrapy.pipelines.images.ImagesPipeline`) wired up declaratively
  instead of called directly.
- Full details, including how to run it and what it does differently
  from `pokemondb_scraper.py`, are in `pokemon_scrapy/README.md`.

## Compiling the full dataset (`compile_pokedex.py`)

`compile_pokedex.py` is the "download everything" exercise: it builds the
master list of all 721 Generation 1-6 species from PokeAPI's
`/generation/{1..6}` endpoints, then for every species, calls
`requests_basics`-style PokeAPI logic and `pokemondb_scraper.scrape_pokemon()`
+ `download_artwork()`, and writes one combined row to `pokedex.csv`.

- **"721", not "800"**: read-write-data/pokemon.csv (a different stage)
  has 800 rows for the same generations because it includes alternate
  forms (Mega Evolutions, etc.) as separate rows. Those don't have a
  name/slug that lines up cleanly across PokeAPI, pokebase, and
  pokemondb.net - pokemondb.net in particular gives Mega forms no page
  of their own, they're a section partway down their base species' page
  - so mapping them consistently across three sources was out of scope
  here. `compile_pokedex.py` covers every base species; alternate forms
  are not included.
- **Long-running, on purpose politely so**: pokemondb.net's requested
  2-second crawl-delay applies per page and per not-yet-downloaded
  image, so a full first run takes on the order of 45-60 minutes. This
  is a deliberate consequence of respecting the same crawl-delay
  `pokemondb_scraper.py` does, not a bug to fix by lowering it.
- **Resumable**: every row is written to `pokedex.csv` and flushed
  immediately after that species is fetched, and `compile_pokedex()`
  skips any name already present in the CSV on the next run. Interrupt
  it any time (Ctrl+C) and re-running the script picks up where it left
  off instead of starting over.
- **Partial failures don't drop a row**: PokeAPI and pokemondb.net are
  each wrapped in their own `try`/`except`, so if one source fails for a
  species (e.g. a name mismatch between the two sites), the row still
  gets the other source's fields, with the failure recorded in that
  row's `fetch_issues` column rather than silently producing a blank
  or, worse, skipping the row entirely.
- **Default-variety fallback**: a handful of species (e.g. `deoxys`,
  which has `deoxys-normal`/`-attack`/`-defense`/`-speed` forms) have no
  plain PokeAPI `pokemon` resource under the species name itself.
  `resolve_default_variety_name()` only runs as a fallback after the
  direct lookup 404s, and asks the species resource which variety is
  `is_default`.
- **`--limit N`** runs only the first N species (national dex order) -
  useful for a quick trial without committing to the full runtime.

## Testing

`tests/test_pokemondb_scraper.py` tests `parse_pokemon_page()` - the
BeautifulSoup parsing logic - against a saved fixture
(`tests/fixtures/bulbasaur.html`, a trimmed excerpt of the real page)
rather than a live network call, so the tests are fast and don't depend
on pokemondb.net being reachable. The other three modules aren't unit
tested: they're thin wrappers around a REST call, which is more useful to
see run for real (`main.py`) than to test against a mocked response.

Run from the repo root with `.venv` active:

```bash
pytest data-scrape/tests
```

## Running

Add the new dependencies first, if you haven't already synced the venv:

```bash
.venv/Scripts/python.exe -m piptools sync requirements.txt
```

Then, from the repo root with `.venv` active:

```bash
python data-scrape/main.py
```

Or run any single module's own demo the same way, e.g.
`python data-scrape/pokemondb_scraper.py`.

To compile the full dataset (see "Compiling the full dataset" above for
what this actually does and how long it takes):

```bash
python data-scrape/compile_pokedex.py            # all 721 species
python data-scrape/compile_pokedex.py --limit 20 # a quick trial run
```

For the Scrapy project, see `pokemon_scrapy/README.md`'s own "Running"
section - it's run with the `scrapy` CLI from inside `pokemon_scrapy/`,
not with `python`.
