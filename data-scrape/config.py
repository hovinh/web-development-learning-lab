"""Shared constants for the data-scrape stage.

Every module in this stage that makes an HTTP request (to PokeAPI or to
pokemondb.net) sends this User-Agent instead of relying on whatever
`requests`/`urllib` sends by default. Two reasons:

1. It's honest: a server can tell a script is a script anyway, so a
   descriptive UA (what this is, who to contact) is more transparent than
   pretending to be a browser. Spoofing a browser UA to dodge a block is
   the part to avoid, not custom UAs in general.
2. It's occasionally necessary: PokeAPI's CDN returns 403 Forbidden for
   Python's *bare* `urllib` default User-Agent ("Python-urllib/3.x"),
   though it happily accepts `requests`' default ("python-requests/2.x")
   or this explicit one. Sites vary, so setting your own UA is the safer
   habit regardless of which HTTP client you're using.
"""

USER_AGENT = (
    "web-development-learning-lab/1.0 "
    "(educational project; contact hovinh39@gmail.com)"
)
