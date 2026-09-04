"""Lets tests/ import this stage's top-level modules (e.g. `process_pokedex`).

Same reasoning as data-scrape/conftest.py: pytest's default "prepend"
import mode adds a conftest.py's own directory to sys.path when it
discovers it, which is enough to make `data-process/*.py` importable
from `data-process/tests/` without a package on either side.
"""
