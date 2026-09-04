"""Seed the database with 20 sample News rows for local development.

Run with:

    python manage.py seed_news

Same pattern as movie/management/commands/seed_movies.py - a
management command instead of a one-off script, so the seed data is a
real, re-runnable file. See that command's docstring for why.
"""

import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from news.models import News

# 20 short, clearly-fictional site-announcement style stories (not real
# news) - enough sample data to see the "most recent first" ordering
# actually do something. Each one gets its own date, one day apart, so
# the list has 20 distinct positions to sort into.
SAMPLE_HEADLINES = [
    ("Site launched", "Welcome to Movie Reviews - our very first day online."),
    ("Home page redesigned", "Refreshed the home page layout with a cleaner look."),
    ("Bootstrap added", "The site now uses Bootstrap for styling forms and buttons."),
    ("Search added", "You can now search movies by title from the home page."),
    ("Mailing list opened", "Sign up for updates using the new mailing list form."),
    ("Movie database launched", "Movies now have their own model with posters."),
    ("Admin site enabled", "Staff can now manage movies from the Django admin."),
    ("10 movies added", "Seeded the catalogue with 10 classic movies to start."),
    ("Movie cards on home page", "Movies now display as cards with posters and info."),
    ("Search now filters movies", "The search box now filters the movie list by title."),
    ("News section planned", "We're working on a news section for site updates."),
    ("News model created", "News stories can now be stored with a headline and body."),
    ("News admin support", "Staff can now publish news stories from the admin site."),
    ("First news stories published", "Twenty sample stories were added to try out the feed."),
    ("Sorting improved", "News stories are now sorted with the most recent first."),
    ("Navigation updated", "Added a News link to the site's main navigation."),
    ("Bug fixes", "Cleaned up a few rough edges across the site's templates."),
    ("Performance check", "Confirmed pages still load quickly with more sample data."),
    ("Feedback welcome", "Let us know what you'd like to see on the site next."),
    ("Thanks for visiting", "More features are on the way - check back soon."),
]


class Command(BaseCommand):
    help = "Creates 20 sample News rows, one per day, most recent dated today."

    def handle(self, *args, **options):
        today = timezone.localdate()
        created_count = 0

        # Walk the list in reverse so the *last* headline above ends up
        # dated today (offset 0) and the first is the oldest (offset
        # 19) - reads top-to-bottom in SAMPLE_HEADLINES as "in the
        # order these things happened".
        total = len(SAMPLE_HEADLINES)
        for index, (headline, body) in enumerate(SAMPLE_HEADLINES):
            days_ago = total - 1 - index
            story_date = today - datetime.timedelta(days=days_ago)

            # get_or_create by headline so re-running this command
            # doesn't create duplicates - same pattern as seed_movies.
            story, created = News.objects.get_or_create(
                headline=headline,
                defaults={"body": body, "date": story_date},
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {story.headline} ({story.date})")
            else:
                self.stdout.write(f"Skipped (already exists): {story.headline}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done - {created_count} news item(s) created, "
                f"{total - created_count} already existed."
            )
        )
