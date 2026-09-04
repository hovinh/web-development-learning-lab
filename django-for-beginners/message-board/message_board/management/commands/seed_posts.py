"""Seed the database with 3 sample Post rows for local development.

Run with:

    python manage.py seed_posts

Same pattern as django-impatient/moviereviews's seed_movies.py /
seed_news.py commands - a management command instead of a one-off
script, so the seed data is a real, re-runnable file rather than
something typed once into the admin site and then forgotten.
"""

from django.core.management.base import BaseCommand

from message_board.models import Post

SAMPLE_POSTS = [
    "Hello, world!",
    "This is my first Django project.",
    "I'm thinking about what to build next.",
]


class Command(BaseCommand):
    help = "Creates 3 sample Post rows."

    def handle(self, *args, **options):
        created_count = 0

        # get_or_create by text so re-running this command doesn't
        # create duplicates.
        for text in SAMPLE_POSTS:
            post, created = Post.objects.get_or_create(text=text)
            if created:
                created_count += 1
                self.stdout.write(f"Created: {post.text}")
            else:
                self.stdout.write(f"Skipped (already exists): {post.text}")

        total = len(SAMPLE_POSTS)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done - {created_count} post(s) created, "
                f"{total - created_count} already existed."
            )
        )
