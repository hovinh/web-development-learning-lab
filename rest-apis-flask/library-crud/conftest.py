"""Lets tests/ import this stage's top-level modules (e.g. `app`, `models`).

Same reasoning as the other stages' conftest.py: pytest's default
"prepend" import mode adds a conftest.py's own directory to sys.path when
it discovers it, which is enough to make library-crud/*.py importable
from library-crud/tests/ without a package on either side.
"""
