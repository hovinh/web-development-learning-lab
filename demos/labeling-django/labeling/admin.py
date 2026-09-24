from django.contrib import admin

from .models import Item, Label

# Registering both models with list_display/list_filter is what makes
# "admins see everyone's labels and manage users" true with zero
# hand-written views or templates - see demos/labeling-django/README.md's
# admin callout. Compare demos/labeling-fastapi-react/, where an
# equivalent back office would have to be built by hand.


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "model_label", "model_score", "assigned_to")
    list_filter = ("model_label", "assigned_to")
    search_fields = ("text",)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "reviewer", "decision", "corrected_label", "created_at")
    list_filter = ("decision", "reviewer")
