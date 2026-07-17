# Scrapy settings for pokemon_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "pokemon_scrapy"

SPIDER_MODULES = ["pokemon_scrapy.spiders"]
NEWSPIDER_MODULE = "pokemon_scrapy.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent.
# Same reasoning as data-scrape/config.py's USER_AGENT one level up: an
# honest, descriptive UA rather than a spoofed browser one.
USER_AGENT = (
    "pokemon-scrapy-learning-lab/1.0 "
    "(educational project; contact hovinh39@gmail.com)"
)

# Obey robots.txt rules. This is the Scrapy-native equivalent of the
# manual "check robots.txt, respect Crawl-delay" work
# pokemondb_scraper.py does by hand (see its module docstring) - Scrapy's
# RobotsTxtMiddleware fetches and checks robots.txt automatically, and
# refuses to crawl a disallowed URL before this spider ever sees it.
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings.
# pokemondb.net/robots.txt asks for a 2-second Crawl-delay between
# requests for a generic user agent - DOWNLOAD_DELAY is Scrapy's
# equivalent of pokemondb_scraper.py's manual `time.sleep(CRAWL_DELAY_SECONDS)`.
# CONCURRENT_REQUESTS_PER_DOMAIN = 1 makes sure that delay is actually
# respected end-to-end - Scrapy is concurrent by default, and a delay
# means little if multiple requests still go out to the same domain at once.
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "pokemon_scrapy.middlewares.PokemonScrapySpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "pokemon_scrapy.middlewares.PokemonScrapyDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines.
# Pipelines run in ascending order of their number for every item a
# spider yields:
#   100 - DropIncompletePokemonPipeline (this project's own pipeline,
#         in pipelines.py): drops any item missing a required field
#         before it reaches anything downstream.
#   1   - scrapy.pipelines.images.ImagesPipeline (built in to Scrapy):
#         downloads the URL(s) in each item's `image_urls` field and
#         fills in `images` with the saved path(s) - the Scrapy-native
#         equivalent of pokemondb_scraper.download_artwork().
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "pokemon_scrapy.pipelines.DropIncompletePokemonPipeline": 100,
    "scrapy.pipelines.images.ImagesPipeline": 1,
}

# Where ImagesPipeline saves downloaded artwork. Kept inside this Scrapy
# project folder rather than reusing data-scrape/images/, so this
# exercise's output doesn't collide with pokemondb_scraper.py's.
IMAGES_STORE = "images"

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable HTTP caching - Scrapy's own equivalent of
# cached_requests_demo.py's requests_cache.CachedSession. Re-running this
# spider while developing it replays cached responses from HTTPCACHE_DIR
# instead of re-fetching (and re-waiting out DOWNLOAD_DELAY for) pages
# it's already crawled.
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 60 * 60 * 24  # 1 day - this data barely changes
HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
