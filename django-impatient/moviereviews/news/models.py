from django.db import models


class News(models.Model):
    headline = models.CharField(max_length=200)

    # TextField (vs CharField) has no length limit - matches Movie.description
    # in movie/models.py, same reasoning: free-form prose, not a short label.
    body = models.TextField()

    # DateField (not DateTimeField) - "date" here means "the day this
    # story is dated", not an exact publish timestamp. Sorting by this
    # (see news/views.py's index()) still works fine at day granularity
    # for a learning-lab news feed.
    date = models.DateField()

    class Meta:
        # Sets the *default* ordering for News.objects.all() etc., so
        # "most recent first" is the natural order even if a view
        # forgets to say so explicitly. news/views.py's index() still
        # orders explicitly (see its comment) so that intent isn't
        # silently dependent on this default.
        ordering = ["-date"]

    def __str__(self):
        # Same reasoning as Movie.__str__() in movie/models.py - without
        # this, admin/shell would show "News object (1)" instead of the
        # headline.
        return self.headline
