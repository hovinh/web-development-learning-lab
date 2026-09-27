"""Lets tests/ import this stage's top-level modules (`content`, `theme`).

Same reasoning as demos/long-jobs/conftest.py: pytest's default "prepend"
import mode adds a conftest.py's own directory to sys.path when it
discovers it, which is enough to make slides/*.py importable from
slides/tests/ without a package on either side.
"""
