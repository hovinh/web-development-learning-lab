# Build prompt: Demo 3 — long-running jobs (Huey + SQLite)

Saved for future reference — hand this to a fresh Claude Code session to rebuild this demo from
scratch (e.g. in another repo with the same conventions). See [`README.md`](README.md) for what
was actually built and how to run it.

---

Build a minimal FastAPI demo at demos/long-jobs/ showing the blocking-request-vs-background-job
pattern, using Huey with SQLite storage (no Redis, no Celery) - the Windows-safe default from
docs like .claude/skills/web-stack-advisor/references/background-jobs.md. Deliberately its own
tiny app, not bolted onto the labeling demos, so it reads without auth/admin noise.

Files:
- database.py: raw sqlite3 (not SQLAlchemy - one small table, doesn't earn an ORM).
  get_connection() opens a fresh connection per call (check_same_thread=False, since the FastAPI
  process and the Huey consumer process are different threads/processes touching the same file).
  init_db() creates a `jobs` table (id, status, progress, total, created_at) if missing.
- jobs.py: create_job(total), update_job(job_id, status=None, progress=None), get_job(job_id) ->
  dict|None. This table is the ONLY thing the web process and the worker process share.
- tasks.py: `huey = SqliteHuey(filename="huey.sqlite3")`, and a `@huey.task()` rescore_dataset(job_id)
  that walks demos/sample-data/predictions.json (create this shared file first if it doesn't
  exist - 30 rows of {id, text, model_label, model_score}), time.sleep()-ing per row (~0.5s) to
  simulate real model-inference work, calling jobs.update_job(progress=...) after each row.
- app.py: `@asynccontextmanager` lifespan calling init_db() at startup (not the deprecated
  @app.on_event). Import tasks as a module (not `from tasks import X`) so tests can monkeypatch
  tasks.SECONDS_PER_ROW/tasks.huey.immediate without the route holding a stale copy. Routes:
  POST /rescore-blocking (does the whole loop inline - THE PROBLEM, comment it as such),
  POST /jobs/rescore (creates a queued job row, calls the Huey task - which only enqueues, does
  not run it - returns job_id immediately), GET /jobs/{id} (reads the table, 404 if missing),
  GET / (serves static/index.html).
- static/index.html: plain vanilla JS (not jQuery - this page makes exactly two fetch calls and
  does no DOM traversal beyond setting a few text values by id, so jQuery's actual value isn't
  exercised; write a "Why plain fetch, not jQuery" justification in the README since
  docs/javascript.md defaults to jQuery). Two buttons: one hits /rescore-blocking and visibly
  hangs; one hits /jobs/rescore, gets a job id back immediately, then polls GET /jobs/{id} every
  2s and draws a progress bar via a <progress> element.
- conftest.py (empty, just makes the stage's modules importable from tests/, matching
  rest-apis-flask/library-crud/conftest.py's pattern) + tests/test_jobs.py: pytest fixture that
  monkeypatches database.DB_PATH to a tmp_path file for isolation. Test jobs.py's create/update/
  read directly. Test GET /jobs/{unknown} is 404. For any test that goes through
  POST /jobs/rescore or calls tasks.rescore_dataset directly, monkeypatch BOTH
  tasks.SECONDS_PER_ROW to 0 AND tasks.huey.immediate to True - immediate mode runs the task
  synchronously in-process instead of writing it into the real, persistent huey.sqlite3 queue
  file, which otherwise leaks a stray task that a later real consumer run picks up and updates
  the wrong (already-deleted) job row against. This is a real trap, not hypothetical - verify it
  doesn't happen by checking no huey.sqlite3-related task execution shows up when you later run a
  real consumer after the test suite.

Add to the repo root requirements.in (pip-tools workflow): fastapi, uvicorn, huey, httpx (for
TestClient). Add demos/long-jobs/jobs.sqlite3 and demos/long-jobs/huey.sqlite3 to .gitignore.

Critical thing to verify, not just assert in the README: start the API AND a real Huey consumer
side by side and confirm progress actually advances. The command is:

    huey_consumer tasks.huey -k thread

NOT `huey_consumer.py` - check the installed huey package's actual console_scripts entry point
name (`python -c "import importlib.metadata as m; print(m.distribution('huey').entry_points)"`)
before writing the README, since many Huey tutorials write it with `.py` but the entry point may
be registered as plain `huey_consumer`, which on Windows means only `huey_consumer.exe` exists in
.venv/Scripts - `huey_consumer.py` isn't a real command there. -k thread is required on Windows
regardless, since the default process-pool workers use os.fork(), which doesn't exist there -
confirm the consumer actually starts and processes the queue with that flag before writing it up
as fact.

Write demos/long-jobs/README.md: "why before how" (the blocking route side by side with the
fix), "Why Huey on SQLite", the exact verified consumer command, "Why plain fetch not jQuery",
and a two-terminal run block (uvicorn, then the consumer command).
