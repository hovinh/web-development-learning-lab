from django.db import models


class Post(models.Model):
    # TextField rather than CharField - no max_length ceiling, and a
    # message board post is prose, not a short label.
    text = models.TextField()

    def __str__(self):
        # Shown in the Django admin's post list and anywhere else a
        # Post gets stringified - without this, admin would just show
        # "Post object (1)" for every row.
        return self.text
