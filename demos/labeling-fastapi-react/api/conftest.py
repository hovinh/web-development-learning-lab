"""Lets tests/ import this stage's top-level modules (e.g. `main`, `models`).

Same reasoning as rest-apis-flask/library-crud/conftest.py: pytest's
default "prepend" import mode adds a conftest.py's own directory to
sys.path when it discovers it, which is enough to make
labeling-fastapi-react/api/*.py importable from api/tests/ without a
package on either side.
"""
