"""Populate labeling.db with the same demo users and items as
demos/labeling-django/labeling/management/commands/seed_demo.py - same
usernames, same passwords, same sample-data rows assigned the same
round-robin way, so a ticket with a given id means the same thing in
both demos and the two are a fair head-to-head (see
demos/sample-data/README.md).

Run this once before starting the API - see README.md's "Seeding" section.
Drops and recreates every table on each run: this is fixed demo data
fully reproducible from this file, not something meant to persist or
migrate across runs, same reasoning as
rest-apis-flask/library-crud/seed.py.

Run with:

    python demos/labeling-fastapi-react/api/seed.py
"""

from __future__ import annotations

import json

from database import STAGE_DIR, make_session_factory
from models import Base, Item, User
from security import hash_password

# demos/sample-data/ is two levels up from this file
# (labeling-fastapi-react/api/) - see demos/sample-data/README.md for
# why this file is shared with labeling-django instead of each demo
# having its own copy.
SAMPLE_DATA_PATH = STAGE_DIR.parent.parent / "sample-data" / "predictions.json"

# (username, password, is_admin) - identical to
# demos/labeling-django/labeling/management/commands/seed_demo.py's
# DEMO_USERS, so both demos' /admin (Django) and admin@... (FastAPI)
# logins are the same credentials.
DEMO_USERS = [
    ("admin", "demo-admin-pw", True),
    ("alice", "demo-alice-pw", False),
    ("bob", "demo-bob-pw", False),
]

REVIEWER_USERNAMES = ["alice", "bob"]


def seed() -> None:
    session_factory = make_session_factory()
    db = session_factory()

    try:
        # Fixed, fully reproducible demo data - drop and recreate rather
        # than trying to merge with whatever's already there.
        Base.metadata.drop_all(db.get_bind())
        Base.metadata.create_all(db.get_bind())

        users_by_name = {}
        for username, password, is_admin in DEMO_USERS:
            user = User(
                username=username, hashed_password=hash_password(password), is_admin=is_admin
            )
            db.add(user)
            users_by_name[username] = user
        db.flush()  # assigns ids without a full commit, so items below can reference them

        reviewers = [users_by_name[name] for name in REVIEWER_USERNAMES]

        rows = json.loads(SAMPLE_DATA_PATH.read_text())
        for index, row in enumerate(rows):
            # Round-robin by position, matching seed_demo.py exactly.
            reviewer = reviewers[index % len(reviewers)]
            db.add(
                Item(
                    id=row["id"],
                    text=row["text"],
                    model_label=row["model_label"],
                    model_score=row["model_score"],
                    assigned_to_id=reviewer.id,
                )
            )

        db.commit()
    finally:
        db.close()

    print(
        f"Seeded {len(DEMO_USERS)} users and {len(json.loads(SAMPLE_DATA_PATH.read_text()))} "
        f"items into demos/labeling-fastapi-react/api/labeling.db"
    )
    print("Demo logins: admin/demo-admin-pw, alice/demo-alice-pw, bob/demo-bob-pw")


if __name__ == "__main__":
    seed()
