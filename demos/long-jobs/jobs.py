"""The job-status table: create a job row, update its progress, read it back.

This is step 3 of the pattern this whole demo teaches ("status and
result are stored - a table, a file, a cache"): app.py's queued endpoint
creates a row here before returning, tasks.py's background task updates
it as it works, and app.py's GET /jobs/{id} just reads it. Neither the
web process nor the worker process needs to talk to the other directly -
the table is the only thing they share.
"""

from database import get_connection

STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_DONE = "done"
STATUS_FAILED = "failed"


def create_job(total: int) -> int:
    """Insert a new job row with status=queued, progress=0. Returns its id."""
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO jobs (status, progress, total) VALUES (?, 0, ?)",
            (STATUS_QUEUED, total),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update_job(job_id: int, *, status: str | None = None, progress: int | None = None) -> None:
    """Update whichever of status/progress was passed, leaving the other alone.

    Called repeatedly by tasks.py's rescore task as it walks the rows -
    each call is its own short connection/commit so the row is visible
    to a concurrent GET /jobs/{id} poll immediately, not just once the
    whole task finishes.
    """
    connection = get_connection()
    try:
        if status is not None:
            connection.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
        if progress is not None:
            connection.execute("UPDATE jobs SET progress = ? WHERE id = ?", (progress, job_id))
        connection.commit()
    finally:
        connection.close()


def get_job(job_id: int) -> dict | None:
    """Read one job row as a dict, or None if job_id doesn't exist."""
    connection = get_connection()
    try:
        row = connection.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()
