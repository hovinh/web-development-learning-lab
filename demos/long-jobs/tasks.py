"""The Huey worker: a SQLite-backed task queue, and the rescore job itself.

SqliteHuey stores the task queue in a SQLite file (huey.sqlite3, created
next to this file) instead of needing Redis - see README.md's "Why Huey
on SQLite" section for why that's the right default on a Windows laptop
with nothing else installed. This module only *defines* the queue and
task; a separate process actually runs it:

    huey_consumer tasks.huey -k thread

-k thread (not the default process pool) is required on Windows - see
README.md for why.
"""

import json
import time
from pathlib import Path

from huey import SqliteHuey

import jobs

STAGE_DIR = Path(__file__).parent
huey = SqliteHuey(filename=str(STAGE_DIR / "huey.sqlite3"))

# Reuses the same 30-row dataset as demos/labeling-django and
# demos/labeling-fastapi-react (see demos/sample-data/README.md) - this
# job "re-scores" that same batch of tickets with a new (fictional)
# model, one row at a time.
SAMPLE_DATA_PATH = STAGE_DIR.parent / "sample-data" / "predictions.json"

# Seconds of fake work per row - long enough that watching the progress
# bar move (or the blocking endpoint hang) is obvious, short enough that
# the whole demo job finishes in well under a minute.
SECONDS_PER_ROW = 0.5


@huey.task()
def rescore_dataset(job_id: int) -> None:
    """Walk every row in the sample dataset, "re-scoring" it, and update
    jobs.py's job-status table as it goes.

    This runs in the huey consumer process/thread, not in the FastAPI
    request that enqueued it (see app.py's POST /jobs/rescore) - that
    separation is step 2 of the pattern this demo teaches ("the job runs
    elsewhere").
    """
    rows = json.loads(SAMPLE_DATA_PATH.read_text())

    jobs.update_job(job_id, status=jobs.STATUS_RUNNING)

    for index, _row in enumerate(rows, start=1):
        # A real re-scoring job would call a model here; this demo only
        # needs something that takes real wall-clock time so the
        # progress bar visibly moves and the blocking counter-example
        # visibly hangs.
        time.sleep(SECONDS_PER_ROW)
        jobs.update_job(job_id, progress=index)

    jobs.update_job(job_id, status=jobs.STATUS_DONE)
