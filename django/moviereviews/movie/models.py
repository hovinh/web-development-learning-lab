from django.db import models


# Each Model subclass maps to one database table; each field below maps
# to one column. Django's migration system (see django/README.md's log)
# reads this class to generate the SQL that creates/updates that table -
# the class itself is the single source of truth for the schema, you
# never hand-write CREATE TABLE for it.
class Movie(models.Model):
    title = models.CharField(max_length=200)

    # TextField (vs CharField) has no length limit - right choice for
    # free-form prose like a plot summary.
    description = models.TextField()

    # ImageField validates that the uploaded file is actually a valid
    # image (via Pillow, see requirements.in) and stores it under
    # MEDIA_ROOT/movie_images/ (see moviereviews/settings.py's
    # MEDIA_ROOT/MEDIA_URL). The database column itself only holds the
    # relative file path, not the image bytes.
    image = models.ImageField(upload_to="movie_images/")

    # e.g. a link to the trailer or an external review. URLField is a
    # CharField that also validates the value looks like a URL.
    url = models.URLField()

    def __str__(self):
        # Without this, Django's admin site and the Python shell would
        # show unhelpful "Movie object (1)" instead of the title.
        return self.title
