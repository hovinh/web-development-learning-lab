"""Seed the database with 10 sample Movie rows for local development.

Run with:

    python manage.py seed_movies

A Django "management command" (any module under
management/commands/<name>.py) is the idiomatic way to script one-off
or repeatable admin tasks like this - it reuses manage.py's normal
settings/DB setup, unlike a bare script you'd run with plain `python`.
"""

import hashlib
import io
import textwrap

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from movie.models import Movie

# 10 well-known movies, with short original one-line descriptions (not
# copied from IMDb/any other source) - just enough sample data to see
# the site and admin working with something more real than "Movie 1".
# `url` is a placeholder (this app doesn't actually own these movies'
# pages) rather than a guessed link to a real external site.
SAMPLE_MOVIES = [
    {
        "title": "The Shawshank Redemption",
        "description": (
            "A banker wrongly convicted of murder forms an unlikely "
            "friendship with a fellow inmate over decades in prison."
        ),
    },
    {
        "title": "The Godfather",
        "description": (
            "The aging patriarch of a powerful crime family transfers "
            "control of his empire to his reluctant son."
        ),
    },
    {
        "title": "The Dark Knight",
        "description": (
            "Batman faces his greatest psychological and physical test "
            "when a criminal mastermind known as the Joker wreaks havoc "
            "on Gotham."
        ),
    },
    {
        "title": "Pulp Fiction",
        "description": (
            "The lives of two hitmen, a boxer, and a gangster's wife "
            "intertwine in four tales of violence and redemption."
        ),
    },
    {
        "title": "Forrest Gump",
        "description": (
            "A slow-witted but kind-hearted man from Alabama "
            "unwittingly influences several defining historical events."
        ),
    },
    {
        "title": "Inception",
        "description": (
            "A thief who steals corporate secrets through dream-sharing "
            "technology is given the inverse task of planting an idea."
        ),
    },
    {
        "title": "The Matrix",
        "description": (
            "A computer hacker learns the true nature of his reality "
            "and his role in the war against its controllers."
        ),
    },
    {
        "title": "Interstellar",
        "description": (
            "A team of explorers travels through a wormhole in search "
            "of a new home for humanity as Earth becomes uninhabitable."
        ),
    },
    {
        "title": "Parasite",
        "description": (
            "Greed and class discrimination threaten the newly formed "
            "symbiotic relationship between a wealthy family and a poor "
            "one."
        ),
    },
    {
        "title": "Spirited Away",
        "description": (
            "During her family's move to a new home, a sullen "
            "10-year-old girl wanders into a world ruled by spirits."
        ),
    },
]

POSTER_SIZE = (300, 450)  # a roughly 2:3 movie-poster aspect ratio


def make_placeholder_poster(title: str) -> ContentFile:
    """Generate a simple solid-colour poster image with the title on it.

    There's no real artwork for these sample entries, and Movie.image
    is a required field - this generates something valid to satisfy it
    (using Pillow, already a repo dependency - see requirements.in)
    rather than leaving the field empty or faking a download.
    """
    # Derive a stable, distinct-looking colour per title (not random,
    # so re-running this command produces the same poster each time)
    # from a hash of the title text.
    digest = hashlib.md5(title.encode("utf-8")).digest()
    background = (digest[0], digest[1], digest[2])

    image = Image.new("RGB", POSTER_SIZE, color=background)
    draw = ImageDraw.Draw(image)
    # load_default()'s `size` argument (Pillow >= 10) swaps in a scaled
    # bitmap font - without it, load_default() renders text almost too
    # small to read at this image size.
    font = ImageFont.load_default(size=28)

    # Wrap the title so long ones don't run off the edge of the poster.
    wrapped_title = "\n".join(textwrap.wrap(title, width=18))
    text_box = draw.multiline_textbbox((0, 0), wrapped_title, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    position = (
        (POSTER_SIZE[0] - text_width) / 2,
        (POSTER_SIZE[1] - text_height) / 2,
    )
    draw.multiline_text(
        position, wrapped_title, font=font, fill="white", align="center"
    )

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Creates 10 sample Movie rows (with generated placeholder posters)."

    def handle(self, *args, **options):
        created_count = 0
        for movie_data in SAMPLE_MOVIES:
            slug = movie_data["title"].lower().replace(" ", "-")

            # get_or_create by title so running this command again
            # (e.g. after `manage.py flush`) doesn't create duplicates.
            movie, created = Movie.objects.get_or_create(
                title=movie_data["title"],
                defaults={
                    "description": movie_data["description"],
                    "url": f"https://example.com/movies/{slug}",
                },
            )
            if not created:
                self.stdout.write(f"Skipped (already exists): {movie.title}")
                continue

            poster = make_placeholder_poster(movie_data["title"])
            # image.save(name, content, save=False) writes the file to
            # MEDIA_ROOT/movie_images/ and sets the field's value, but
            # `save=False` means it doesn't also re-save the model row -
            # the movie.save() below does that once, for both changes.
            movie.image.save(f"{slug}.jpg", poster, save=False)
            movie.save()

            created_count += 1
            self.stdout.write(f"Created: {movie.title}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done - {created_count} movie(s) created, "
                f"{len(SAMPLE_MOVIES) - created_count} already existed."
            )
        )
