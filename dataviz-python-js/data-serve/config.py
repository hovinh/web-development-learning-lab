"""Shared paths for the data-serve stage.

Everything here points at data-process's output by default - this stage
doesn't scrape or clean anything itself, it only serves what
data-process already produced. Both the file and sqlite backends accept
overrides for these paths (see repositories.py), which is what lets
tests/test_app.py point at a small synthetic dataset instead of the real
~700-Pokemon one.
"""

from pathlib import Path

STAGE_DIR = Path(__file__).parent
DATA_PROCESS_DIR = STAGE_DIR.parent / "data-process"

POKEDEX_JSON_PATH = DATA_PROCESS_DIR / "pokedex.json"
IMAGES_DIR = DATA_PROCESS_DIR / "images"

# The sqlite backend's own database - lives in this stage, not
# data-process, since it's data-serve's derived copy (built by
# load_sqlite.py), not something data-process produces itself.
SQLITE_DB_PATH = STAGE_DIR / "pokedex.db"
SQLITE_DATABASE_URI = f"sqlite:///{SQLITE_DB_PATH}"
