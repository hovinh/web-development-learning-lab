"""SQLAlchemy engine/session setup.

`make_session_factory()` (not one bare module-level engine) is what lets
tests/test_api.py point this same schema at an isolated, temporary
database instead of labeling.db - same reasoning as
rest-apis-flask/library-crud/app.py's create_app(sqlite_uri=...), and
FastAPI's own documented testing pattern of overriding the `get_db`
dependency (see deps.py) rather than monkeypatching a global.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

STAGE_DIR = Path(__file__).parent
DEFAULT_SQLITE_PATH = STAGE_DIR / "labeling.db"


def make_session_factory(sqlite_path: Path | None = None) -> sessionmaker:
    """Build a fresh engine + session factory bound to `sqlite_path`
    (labeling.db by default), creating any missing tables.

    Base.metadata.create_all() is fine for a demo with a fixed, small
    schema - a real project would use a migration tool (e.g. Alembic)
    instead, so schema changes don't require dropping data. Same caveat
    rest-apis-flask/library-crud/app.py's create_app() carries for its
    own db.create_all() call.
    """
    sqlite_path = sqlite_path or DEFAULT_SQLITE_PATH
    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        # SQLite only allows a connection to be used on the thread that
        # created it by default - FastAPI's docs recommend disabling
        # that check here because each request gets its own short-lived
        # session anyway (see deps.py's get_db), not a connection shared
        # across threads.
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Module-level default, used by the app unless a test overrides
# deps.get_db (see conftest.py) to point at a temporary database instead.
SessionLocal = make_session_factory()
