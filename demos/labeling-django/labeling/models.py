from django.conf import settings
from django.db import models


# Each Model subclass maps to one database table; each field below maps to
# one column. Django's migration system reads this class to generate the
# SQL that creates/updates that table.
class Item(models.Model):
    # The support ticket text a reviewer reads to decide if the model's
    # prediction is correct - see ../../sample-data/README.md.
    text = models.TextField()

    model_label = models.CharField(max_length=50)

    # The model's confidence in model_label, 0-1. FloatField (not a
    # DecimalField) - this is a display value read by a human, not money,
    # so float rounding is a non-issue.
    model_score = models.FloatField()

    # settings.AUTH_USER_MODEL (not a direct `from django.contrib.auth
    # import User` import) is the standard way to reference "whichever
    # user model this project uses" - it's the same built-in User here,
    # but referencing it this way is what Django's own docs recommend, in
    # case a project ever swaps in a custom user model later.
    #
    # null=True: a freshly-loaded item has no reviewer yet until
    # seed_demo assigns it round-robin (see management/commands/
    # seed_demo.py). on_delete=SET_NULL rather than CASCADE - deleting a
    # reviewer account shouldn't delete the items they were assigned,
    # just unassign them.
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_items",
    )

    def __str__(self):
        # Shown in the Django admin's item list - without this, admin
        # would just show "Item object (1)" for every row.
        return f"#{self.id}: {self.text[:60]}"


class Label(models.Model):
    # A reviewer's decision on one Item. Kept as a separate model (rather
    # than fields bolted onto Item) so a later "relabel" or "second
    # opinion" feature would just mean allowing more than one Label per
    # Item, instead of a schema change.
    class Decision(models.TextChoices):
        CORRECT = "correct", "Correct"
        INCORRECT = "incorrect", "Incorrect"
        UNSURE = "unsure", "Unsure"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="labels")

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="labels"
    )

    decision = models.CharField(max_length=20, choices=Decision.choices)

    # Only meaningful when decision == INCORRECT - what the label should
    # have been instead. Left blank otherwise; not modeled as a separate
    # nullable "corrected model" FK because the reviewer types a plain
    # category name here, not necessarily one that reuses Item.model_label's
    # exact set of values.
    corrected_label = models.CharField(max_length=50, blank=True)

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One label per reviewer per item - matches the queue/label_item
        # views below, which always look up "this reviewer's label for
        # this item" as a single row, not a list.
        unique_together = ("item", "reviewer")

    def __str__(self):
        return f"{self.reviewer.username}'s label for item #{self.item_id}: {self.decision}"
