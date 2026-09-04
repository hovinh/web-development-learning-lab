"""Shared paths/config for the library-crud stage.

Same shape as dataviz-python-js/data-serve/config.py's SQLite bits - a
single STAGE_DIR-relative db file, overridable (see app.py's create_app)
so tests point at an isolated temporary database instead of this one.
"""

from pathlib import Path

STAGE_DIR = Path(__file__).parent

SQLITE_DB_PATH = STAGE_DIR / "library.db"
SQLITE_DATABASE_URI = f"sqlite:///{SQLITE_DB_PATH}"
