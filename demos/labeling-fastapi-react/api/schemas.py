"""Pydantic schemas: the request/response shapes main.py's routes validate
against. Compare demos/labeling-django/labeling/forms.py - Django forms
give server-side validation "for free" off the model; here each shape is
declared by hand, the same trade the blog's forms-and-validation row
describes.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    """Returned by POST /auth/login - see security.py's create_access_token()."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class LabelOut(BaseModel):
    # from_attributes=True lets this be built directly from a
    # models.Label ORM instance (label.decision, label.note, ...)
    # instead of a plain dict - Pydantic v2's replacement for v1's
    # `orm_mode`.
    model_config = ConfigDict(from_attributes=True)

    id: int
    decision: str
    corrected_label: str
    note: str
    created_at: datetime


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    model_label: str
    model_score: float


class ItemDetailOut(ItemOut):
    """ItemOut plus the current reviewer's own label for this item, if
    they've already submitted one - the API equivalent of
    demos/labeling-django/labeling/views.py's label_item() looking up
    `existing_label` before rendering the form.
    """

    my_label: LabelOut | None = None


class LabelIn(BaseModel):
    """Body for POST /items/{item_id}/label.

    `decision` is a Literal, not a plain str - FastAPI/Pydantic reject
    any other value with a 422 before main.py's route body ever runs,
    matching demos/labeling-django/labeling/models.py's
    Label.Decision.choices doing the same job at the database/form
    layer instead.
    """

    decision: Literal["correct", "incorrect", "unsure"]
    corrected_label: str = ""
    note: str = ""


class AdminLabelOut(LabelOut):
    """LabelOut plus who reviewed it - only used by the admin routes
    (see main.py's GET /admin/labels), which is the hand-built
    equivalent of demos/labeling-django/labeling/admin.py's
    LabelAdmin.list_display.
    """

    reviewer_username: str
    item_id: int
