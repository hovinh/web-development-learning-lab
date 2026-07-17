"""Lets tests/ import this stage's top-level modules (e.g. `pokemondb_scraper`).

Empty on purpose: pytest's default "prepend" import mode adds a
conftest.py's own directory to sys.path when it discovers it, which is
enough to make `data-scrape/*.py` importable from `data-scrape/tests/`
without a package (`__init__.py`) on either side - the same "flat stage,
no `src/` layout" style the rest of this repo uses.
"""
