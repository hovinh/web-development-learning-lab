"""The labeling schema: User, Item, Label - SQLAlchemy 2.0's typed
declarative style (Mapped[...] / mapped_column), the same task this
demo's Django counterpart models with Item/Label in
demos/labeling-django/labeling/models.py. Compare the two directly -
the schema is intentionally the same shape either way, so what differs
is how much code each stack needs around it (see database.py, deps.py).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)

    # Never the plain-text password - see security.py's hash_password()/
    # verify_password(), the pwdlib-based equivalent of Django's built-in
    # password hashing that this demo has to set up by hand.
    hashed_password: Mapped[str]

    # Stands in for Django's User.is_staff/is_superuser - gates the
    # /admin/* routes in main.py via deps.py's require_admin().
    is_admin: Mapped[bool] = mapped_column(default=False)

    assigned_items: Mapped[list["Item"]] = relationship(back_populates="assigned_to")
    labels: Mapped[list["Label"]] = relationship(back_populates="reviewer")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]
    model_label: Mapped[str]
    model_score: Mapped[float]

    # nullable - matches demos/labeling-django/labeling/models.py's
    # Item.assigned_to(null=True): a freshly-loaded item has no reviewer
    # until seed.py assigns it round-robin.
    assigned_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    assigned_to: Mapped[User | None] = relationship(back_populates="assigned_items")
    labels: Mapped[list["Label"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = (
        # One label per reviewer per item - same rule as
        # demos/labeling-django/labeling/models.py's Label.Meta.unique_together,
        # enforced at the database level here too.
        UniqueConstraint("item_id", "reviewer_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # A plain string, not a SQLAlchemy Enum - schemas.py's Pydantic
    # LabelIn model is what actually restricts this to
    # correct/incorrect/unsure at the API boundary (see its Literal
    # type); the database column just stores whatever passed that
    # check, same division of labour FastAPI's own docs recommend.
    decision: Mapped[str]

    corrected_label: Mapped[str] = mapped_column(default="")
    note: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    item: Mapped[Item] = relationship(back_populates="labels")
    reviewer: Mapped[User] = relationship(back_populates="labels")
