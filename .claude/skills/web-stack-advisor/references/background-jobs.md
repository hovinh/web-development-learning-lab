# Background and long-running jobs

A web request must answer in seconds. Training a model, a big query or a scrape does
not. The pattern is always the same:

1. The request **starts the job** and returns immediately with a job id.
2. The job runs **elsewhere** (another thread, process or machine).
3. Status and result are **stored** (a table, a file, a cache).
4. The page **checks back** (polling `fetch` every few seconds; SSE or websockets later).

## Options (checked September 2026)

| Need | Tool | Notes |
|---|---|---|
| Tiny work after the response (log, send an email) | FastAPI `BackgroundTasks` | Runs in the web process. No persistence or retries; lost if the server restarts. Not for heavy compute |
| Simple queue on one machine | **Huey** | Can store jobs in **SQLite**, so no Redis needed. Good local default |
| Simple queue with Redis | **RQ** | Easiest Redis queue. **No native Windows support** (uses `os.fork`); needs WSL or Linux. Redis-only |
| Full-featured queue, retries, schedules | **Celery** | Windows is unsupported by the project (the `--pool=solo` workaround is dev-only and runs one task at a time). Needs a broker |
| Django's own API | `django.tasks` (Django 6.0) | Standard enqueue API only. **No built-in worker**, no retries, scheduling or persistence. Needs a backend package |
| Recurring jobs | cron, APScheduler, Celery beat | |
| Pipelines and DAGs | Airflow, Prefect, Dagster | The data-engineering answer; keep the web UI as a status page |
| Long compute inside Streamlit/Dash | A thread or subprocess, then poll | Do not block the script run |

## Recommendation for someone working on a Windows laptop

1. Start with **polling plus a job-status table** (a Django model, or a SQLite file).
2. Use **Huey with SQLite storage** for the worker: nothing to install beyond Python.
3. Move to Celery (on Linux/WSL) only when retries and scheduling are needed.
4. For pipeline-style work, use Prefect or Dagster and make the web app a read-only
   status page.

Django 4.x (an older release) has no `django.tasks`; the Django 6.0 API is worth
knowing but does not remove the need for a worker.
