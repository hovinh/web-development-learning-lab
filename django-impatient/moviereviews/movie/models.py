from django.conf import settings
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


class Review(models.Model):
    # ForeignKey (not a plain int) - Django follows this relationship
    # both ways: movie.reviews.all() (via related_name below) lists a
    # movie's reviews without a separate query, and on_delete=CASCADE
    # means deleting a Movie also deletes its reviews, rather than
    # leaving orphaned rows pointing at nothing.
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")

    # settings.AUTH_USER_MODEL (not a direct `from django.contrib.auth
    # import User` import) is the standard way to reference "whichever
    # user model this project uses" - it's the same built-in User here
    # (see accounts/forms.py), but referencing it this way is what
    # Django's own docs recommend, in case a project ever swaps in a
    # custom user model later.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="movie_reviews"
    )

    text = models.TextField()

    # auto_now_add sets this once, at creation, and never again -
    # different from auto_now (used by updated_at below), which
    # overwrites itself on every save().
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # One review per user per movie - keeps "edit your review" an
        # unambiguous action (there's only ever one to find), and
        # matches how most review sites actually work. Enforced at the
        # database level here; movie/views.py's add_review() also
        # checks this before rendering the form, so a user hits a
        # friendly redirect to their existing review instead of a
        # database error.
        unique_together = ("movie", "user")

    def __str__(self):
        return f"{self.user.username}'s review of {self.movie.title}"
