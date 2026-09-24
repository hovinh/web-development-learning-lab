# Demo 3 — long-running jobs

Backs the blog's ["Long-running jobs"](../../blog/web-dev-for-data-people/2026-09-20-web-dev-for-data-people.md)
section and the `web-stack-advisor` skill's
[`background-jobs.md`](../../.claude/skills/web-stack-advisor/references/background-jobs.md).
Deliberately its own minimal app rather than a feature bolted onto [`../labeling-django/`](../labeling-django/README.md)
or [`../labeling-fastapi-react/`](../labeling-fastapi-react/README.md), so this lesson reads
without any auth/admin noise around it — it's a small FastAPI app plus a Huey/SQLite worker, on
the "re-score the dataset with a new model" job the blog's scenario names.

## Why before how

The pattern this demo teaches is always the same four steps: the request **starts the job** and
returns immediately with a job id; the job runs **elsewhere**; status is **stored** (a table);
the page **checks back** (polling). [`app.py`](app.py) makes the "why" concrete by implementing
the broken version first, side by side with the fix:

- `POST /rescore-blocking` — walks all 30 rows of [`../sample-data/predictions.json`](../sample-data/README.md)
  inline, in the request handler, `time.sleep()`-ing to stand in for real model-inference work.
  Click it in the browser and the tab just sits there for ~15 seconds with nothing to show for
  it — no job id, no progress, no way to tell "still working" from "stuck". **This is the
  problem the other three steps below solve.**
- `POST /jobs/rescore` — creates a `queued` row in [`jobs.py`](jobs.py)'s job-status table,
  hands the actual work to [`tasks.py`](tasks.py)'s Huey task, and returns the job id at once.
- `GET /jobs/{id}` — the job's current status/progress, read straight from that table.
- [`static/index.html`](static/index.html) polls `GET /jobs/{id}` every 2 seconds and draws a
  progress bar, so the page stays interactive the entire time the job runs.

## Why Huey on SQLite

`background-jobs.md`'s recommendation for someone on a Windows laptop is "polling plus a
job-status table" and "Huey with SQLite storage" — no Redis, nothing to install beyond Python.
[`tasks.py`](tasks.py) is that: `SqliteHuey(filename="huey.sqlite3")`, no broker process, no
extra service to run alongside the API.

**Verified, not just asserted, on this machine:** Huey's consumer must run with **thread
workers**, not its default process-pool workers, on Windows:

```
huey_consumer tasks.huey -k thread
```

Huey's default worker type (`-k process`) uses `os.fork()` to spawn workers, which doesn't exist
on Windows — the consumer would fail outright without `-k thread`. Run with a real API server and
consumer side by side (see "Run it" below) and `GET /jobs/{id}`'s `progress` field visibly climbs
from 0 to 30 as the consumer works through the queue, confirming this isn't just a documentation
claim.

**Note the command is `huey_consumer`, not `huey_consumer.py`** (many Huey tutorials, including
its own docs, write it with `.py`). The version installed here (see `requirements.txt`) registers
its console-script entry point as plain `huey_consumer` — confirmed via
`importlib.metadata.distribution("huey").entry_points`, not assumed from the docs — so on Windows
pip creates `huey_consumer.exe` in `.venv\Scripts`, and `huey_consumer.py` is simply not a command
that exists. With `.venv` active, `huey_consumer` resolves to it directly.

## Why plain `fetch`, not jQuery

[`docs/javascript.md`](../../docs/javascript.md) prefers jQuery for browser AJAX in this repo,
so this page's plain `fetch` calls are a deliberate deviation. `static/index.html` makes exactly
two HTTP calls and does no DOM traversal or manipulation beyond setting a handful of text/
attribute values on elements already grabbed by id — jQuery's actual value (its selector/
traversal API) isn't exercised by anything on this page. Pulling in a whole library for two
`fetch` calls would add a `<script>` tag and a dependency to explain, without making the thing
this demo is actually about — the start/poll request shape — any clearer. Every other browser-
facing stage in this repo still defaults to jQuery per `docs/javascript.md`; this is a one-page
exception, not a change to that default.

## No seeding needed

Unlike [`../labeling-django/`](../labeling-django/README.md) and
[`../labeling-fastapi-react/`](../labeling-fastapi-react/README.md), this demo has no users and
no database to seed ahead of time — `database.py`'s `init_db()` creates the (empty) `jobs` table
automatically on startup, and each click of a button creates its own job row on demand.

## Run it

Two terminals, both from the repo root with `.venv` active:

```bash
# Terminal 1 - the API
uvicorn app:app --reload --app-dir demos/long-jobs

# Terminal 2 - the worker. -k thread is required on Windows, see above.
# Note: huey_consumer, not huey_consumer.py - see "Why Huey on SQLite" above.
cd demos/long-jobs
huey_consumer tasks.huey -k thread
```

Then open http://127.0.0.1:8000/ and:

1. Click **Start blocking rescore** — the button (and the page) stays stuck for ~15 seconds
   before showing a result.
2. Click **Start queued rescore** — a job id appears immediately, and the progress bar climbs
   from 0/30 to 30/30 as Terminal 2 works through the queue, while the page stays fully
   responsive the whole time.

Tests (no consumer needed — see `tests/test_jobs.py`'s use of Huey's `immediate` testing mode):

```bash
pytest demos/long-jobs/tests
```
