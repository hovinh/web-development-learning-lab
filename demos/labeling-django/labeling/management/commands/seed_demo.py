"""Seed the database with demo users and labeling items.

Run with:

    python manage.py seed_demo

Same pattern as django-for-beginners/message-board's seed_posts.py /
django-impatient/moviereviews's seed_movies.py commands - a management
command instead of a one-off script, so the seed data is a real,
re-runnable file rather than something typed once into the admin site
and forgotten.

Creates one superuser (admin) and two reviewers (alice, bob), then loads
demos/sample-data/predictions.json and assigns each row to a reviewer
round-robin, so both reviewers get roughly half the queue and every row
in the shared dataset ends up assigned to someone.
"""

import json
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from labeling.models import Item

# demos/sample-data/ is three levels up from this file
# (labeling-django/labeling/management/commands/) - see
# demos/sample-data/README.md for why this file is shared with
# labeling-fastapi-react instead of each demo having its own copy.
SAMPLE_DATA_PATH = (
    Path(__file__).resolve().parents[4] / "sample-data" / "predictions.json"
)

# (username, password, is_superuser). Demo-only credentials, never used
# outside a local dev server - see README.md's warning.
DEMO_USERS = [
    ("admin", "demo-admin-pw", True),
    ("alice", "demo-alice-pw", False),
    ("bob", "demo-bob-pw", False),
]

REVIEWER_USERNAMES = ["alice", "bob"]


class Command(BaseCommand):
    help = "Creates demo users (admin, alice, bob) and seeds Items from sample-data/predictions.json."

    def handle(self, *args, **options):
        users_by_name = {}
        for username, password, is_superuser in DEMO_USERS:
            # get_or_create so re-running this command doesn't error on
            # a duplicate username or reset an already-set password.
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"is_staff": is_superuser, "is_superuser": is_superuser},
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"Created user: {username}")
            else:
                self.stdout.write(f"Skipped (already exists): {username}")
            users_by_name[username] = user

        reviewers = [users_by_name[name] for name in REVIEWER_USERNAMES]

        rows = json.loads(SAMPLE_DATA_PATH.read_text())

        created_count = 0
        for index, row in enumerate(rows):
            # Round-robin assignment by list position, not by id - the
            # two are the same here since the sample data's ids are
            # already 1..30 with no gaps, but position is what actually
            # guarantees an even split regardless of id values.
            reviewer = reviewers[index % len(reviewers)]

            item, created = Item.objects.get_or_create(
                id=row["id"],
                defaults={
                    "text": row["text"],
                    "model_label": row["model_label"],
                    "model_score": row["model_score"],
                    "assigned_to": reviewer,
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done - {len(DEMO_USERS)} user(s) ensured, "
                f"{created_count} item(s) created out of {len(rows)} in sample-data."
            )
        )
        self.stdout.write(
            "Demo logins: admin/demo-admin-pw (superuser), "
            "alice/demo-alice-pw, bob/demo-bob-pw"
        )
