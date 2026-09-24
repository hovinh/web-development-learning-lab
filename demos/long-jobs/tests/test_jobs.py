"""Tests for the job-status table (jobs.py) and the FastAPI routes (app.py).

Uses FastAPI's TestClient, so no live server/port is needed - same
in-process approach as rest-apis-flask/library-crud/tests/test_app.py's
Flask test_client(). Every test gets an isolated, temporary jobs table
(the `isolated_db` fixture below) instead of touching this stage's real
jobs.sqlite3.
"""

import pytest
from fastapi.testclient import TestClient

import database
import jobs
import tasks
from app import app


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    # database.get_connection() reads database.DB_PATH fresh on every
    # call (it's a module global, not a captured default argument), so
    # monkeypatching it here is enough to redirect every jobs.py
    # function used by this file at a temporary file for the duration
    # of one test.
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "jobs.sqlite3")
    database.init_db()


@pytest.fixture
def client():
    return TestClient(app)


# ---- jobs.py directly ----


def test_create_update_and_read_a_job():
    job_id = jobs.create_job(total=5)

    job = jobs.get_job(job_id)
    assert job["status"] == jobs.STATUS_QUEUED
    assert job["progress"] == 0
    assert job["total"] == 5

    jobs.update_job(job_id, status=jobs.STATUS_RUNNING, progress=3)

    job = jobs.get_job(job_id)
    assert job["status"] == jobs.STATUS_RUNNING
    assert job["progress"] == 3


def test_get_unknown_job_returns_none():
    assert jobs.get_job(999) is None


# ---- app.py's routes ----


def test_get_job_status_endpoint_404s_for_unknown_job(client):
    response = client.get("/jobs/999")
    assert response.status_code == 404


def test_start_rescore_job_endpoint_creates_and_runs_the_job(client, monkeypatch):
    # huey's "immediate" mode (see the docstring below) also keeps this
    # test from writing a real task into tasks.py's persistent
    # huey.sqlite3 queue file - without it, the task would sit there
    # enqueued against a job id from this test's temporary, since-deleted
    # jobs table, and a real huey_consumer running later would pick
    # it up and update the wrong row. See
    # test_rescore_task_walks_every_row_and_marks_the_job_done for why
    # SECONDS_PER_ROW is dropped to 0 too.
    monkeypatch.setattr(tasks, "SECONDS_PER_ROW", 0)
    monkeypatch.setattr(tasks.huey, "immediate", True)

    response = client.post("/jobs/rescore")
    assert response.status_code == 200

    job_id = response.json()["job_id"]
    job = jobs.get_job(job_id)
    assert job["total"] == 30
    assert job["status"] == jobs.STATUS_DONE
    assert job["progress"] == 30


# ---- tasks.py's rescore_dataset, run synchronously ----


def test_rescore_task_walks_every_row_and_marks_the_job_done(monkeypatch):
    # huey's "immediate" mode runs a @huey.task() function synchronously
    # in the calling process instead of enqueueing it for a separate
    # huey_consumer process to pick up - huey's own documented way to
    # test task logic without actually running a consumer alongside the
    # test suite. SECONDS_PER_ROW is dropped to 0 too, or this test
    # would take len(rows) * 0.5 seconds for real.
    monkeypatch.setattr(tasks, "SECONDS_PER_ROW", 0)
    monkeypatch.setattr(tasks.huey, "immediate", True)

    job_id = jobs.create_job(total=30)
    tasks.rescore_dataset(job_id)

    job = jobs.get_job(job_id)
    assert job["status"] == jobs.STATUS_DONE
    assert job["progress"] == 30
