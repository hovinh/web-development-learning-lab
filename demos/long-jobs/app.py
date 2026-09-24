"""FastAPI app: the blocking counter-example, plus the queued-job version.

## Endpoints

- `GET  /`                  - the demo page (static/index.html): a start
  button, a progress bar, and a "block the server" button.
- `POST /rescore-blocking`  - does the whole rescoring job inline, in the
  request itself. This is the problem the rest of the demo solves - see
  README.md's "Why before how" section.
- `POST /jobs/rescore`      - writes a `queued` row (jobs.py), enqueues
  tasks.py's Huey task, and returns the job id immediately.
- `GET  /jobs/{job_id}`     - the job's current status/progress, read
  straight from the jobs table.

Run with (see README.md for the full two-terminal command):

    uvicorn app:app --reload --app-dir demos/long-jobs
"""

import json
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import jobs
import tasks
from database import init_db

STAGE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once before the app starts accepting requests - init_db()
    # must happen before any request touches the jobs table. FastAPI's
    # current recommended way to do startup/shutdown work (the older
    # @app.on_event("startup") decorator is deprecated).
    init_db()
    yield


# Module-level, not just built inside a function - see
# demos/labeling-fastapi-react/api/main.py for why: a production ASGI
# server imports this module and looks for `app` directly.
app = FastAPI(title="Long-running jobs demo", lifespan=lifespan)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STAGE_DIR / "static" / "index.html")


@app.post("/rescore-blocking")
def rescore_blocking() -> dict:
    """The problem, in one endpoint: this `def` runs the entire rescoring
    loop before returning a response at all. Uvicorn's default worker can
    still serve *other* requests while this one blocks (a plain `def`
    route runs in a worker thread - see FastAPI's docs), but the browser
    tab that made *this* request just sits there for
    len(rows) * tasks.SECONDS_PER_ROW seconds with nothing to show for it
    - no job id, no progress, and no way to know it's still working
    versus stuck.

    Imports `tasks` as a module (not `from tasks import ...`) so
    tests/test_jobs.py can monkeypatch tasks.SECONDS_PER_ROW down to
    something fast without this route holding its own frozen copy of
    the old value.
    """
    rows = json.loads(tasks.SAMPLE_DATA_PATH.read_text())
    for _row in rows:
        time.sleep(tasks.SECONDS_PER_ROW)
    return {"message": "done", "rows_rescored": len(rows)}


@app.post("/jobs/rescore")
def start_rescore_job() -> dict:
    """The fix: create the status row, hand the work to the Huey
    consumer, and respond immediately - the request that starts the job
    and the process that runs it are no longer the same thing.
    """
    rows = json.loads(tasks.SAMPLE_DATA_PATH.read_text())
    job_id = jobs.create_job(total=len(rows))

    # Calling a @huey.task()-decorated function doesn't run it here - it
    # serializes the call into huey's SQLite queue (tasks.py's
    # SqliteHuey) for the huey_consumer process to pick up. This line
    # returns immediately regardless of how long rescore_dataset()
    # itself takes.
    tasks.rescore_dataset(job_id)

    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job_status(job_id: int) -> dict:
    job = jobs.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="No job with that id")
    return job
