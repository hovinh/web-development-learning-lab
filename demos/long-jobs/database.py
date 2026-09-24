"""SQLite connection for the job-status table (see jobs.py).

A plain `sqlite3` connection, not SQLAlchemy - this demo only ever
reads/writes one small table with three simple operations (create,
update progress, read), so an ORM would be more machinery than the task
needs. Compare demos/labeling-fastapi-react/api/database.py, which does
reach for SQLAlchemy because that demo has real relationships (items,
labels, users) to model.
"""

import sqlite3
from pathlib import Path

STAGE_DIR = Path(__file__).parent
DB_PATH = STAGE_DIR / "jobs.sqlite3"


def get_connection() -> sqlite3.Connection:
    """One connection per call, not a shared module-level one.

    huey's task runs in a separate worker process/thread from the
    FastAPI request that created the job row (see tasks.py) - sharing a
    single sqlite3.Connection across threads/processes is unsafe, so
    each caller opens and closes its own short-lived connection instead.
    check_same_thread=False additionally allows a connection opened on
    one thread to be used from another, which is needed for
    huey_consumer's thread-worker mode (see README.md's "Why Huey on
    SQLite" section) even though each connection here is still only
    ever used by the thread that opened it.
    """
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Rows behave like dicts (row["progress"]) instead of plain tuples -
    # much easier to read in jobs.py and app.py than positional indexing.
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the jobs table if it doesn't exist yet.

    Called once at FastAPI startup (see app.py) - fine for a demo with
    one fixed table; a real project would use a migration tool instead
    of a hand-written CREATE TABLE IF NOT EXISTS.
    """
    connection = get_connection()
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                total INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
