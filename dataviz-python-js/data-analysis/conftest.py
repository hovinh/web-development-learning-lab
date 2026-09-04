"""Lets tests/ import this stage's top-level modules (e.g. `charts`).

Same reasoning as data-scrape/conftest.py and data-process/conftest.py:
pytest's default "prepend" import mode adds a conftest.py's own directory
to sys.path when it discovers it, which is enough to make
`data-analysis/*.py` importable from `data-analysis/tests/` without a
package on either side.
"""
