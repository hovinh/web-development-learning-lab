"""FastAPI app: JWT auth + ownership-checked labeling endpoints for the
same triage task demos/labeling-django/ solves with Django's built-ins.

## Endpoints

- `POST /auth/login`          - OAuth2 "password" flow: username +
  password in, a JWT out. See security.py.
- `GET  /items`                - the current reviewer's queue (their
  assigned items only).
- `GET  /items/{item_id}`      - one item, 404 unless it's assigned to
  the current reviewer.
- `POST /items/{item_id}/label`- create or update the current reviewer's
  label for that item. Same 404-unless-owned rule as above.
- `GET  /admin/labels`         - every reviewer's labels, admin-only -
  the hand-built equivalent of opening Django's `/admin/`.

Auth and ownership are the two exhibits this demo backs from the blog's
"Two Real Stacks, One Problem" section - see security.py/deps.py's
docstrings and README.md's "Ownership" section for the actual count of
where each check has to be remembered.

## API docs

With the server running: interactive Swagger UI is at `/docs` - see
README.md's "Manual checks" for driving the whole login -> label flow
from there.

Run with (see README.md for the full two-terminal command):

    uvicorn main:app --reload --app-dir demos/labeling-fastapi-react/api
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Generator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, sessionmaker

import deps
from database import make_session_factory
from models import Item, Label, User
from schemas import AdminLabelOut, ItemDetailOut, LabelIn, LabelOut, Token
from security import create_access_token, verify_password


def _to_item_detail(item: Item, current_user: User) -> ItemDetailOut:
    """Build the API response for one item, including the current
    reviewer's own label if they've already submitted one (see
    schemas.py's ItemDetailOut). `item.labels` is a SQLAlchemy lazy
    relationship - reading it here, while the request's DB session is
    still open, is what triggers that query.
    """
    my_label = next(
        (label for label in item.labels if label.reviewer_id == current_user.id), None
    )
    return ItemDetailOut(
        id=item.id,
        text=item.text,
        model_label=item.model_label,
        model_score=item.model_score,
        my_label=LabelOut.model_validate(my_label) if my_label is not None else None,
    )


def _db_dependency(session_factory: sessionmaker) -> Callable[[], Generator[Session, None, None]]:
    """Build a get_db-shaped dependency bound to `session_factory`, so
    create_app(sqlite_path=...) below can redirect deps.get_db at an
    isolated database without touching deps.py itself.
    """

    def _get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    return _get_db


def create_app(sqlite_path: Path | None = None) -> FastAPI:
    """Build the FastAPI app.

    `sqlite_path` lets tests/test_api.py (via conftest.py) point this
    same app at an isolated, temporary database instead of labeling.db -
    same idiom as rest-apis-flask/library-crud/app.py's
    create_app(sqlite_uri=...).
    """
    app = FastAPI(title="Labeling API (FastAPI + JWT)")

    if sqlite_path is not None:
        session_factory = make_session_factory(sqlite_path)
        app.dependency_overrides[deps.get_db] = _db_dependency(session_factory)

    # Scoped to the Vite dev server's own origin/port (see
    # web/vite.config.js) - a page served from anywhere else can't call
    # this API from a browser. Compare demos/labeling-django/, which
    # needs no CORS config at all because its templates and views are
    # the same origin by construction.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/auth/login", response_model=Token)
    def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(deps.get_db),
    ) -> Token:
        user = db.query(User).filter(User.username == form_data.username).first()
        if user is None or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        return Token(access_token=create_access_token(user.username))

    @app.get("/items", response_model=list[ItemDetailOut])
    def list_my_items(
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db),
    ) -> list[ItemDetailOut]:
        """A reviewer's queue - the list equivalent of
        demos/labeling-django/labeling/views.py's queue(). Unlike
        GET /items/{item_id} and POST /items/{item_id}/label below,
        a *list* endpoint can't reuse deps.get_owned_item (that
        dependency expects a single item_id path parameter), so the
        same "only this reviewer's rows" rule is written again here,
        inline - a second place it has to be remembered, on top of
        get_owned_item's own two call sites.
        """
        items = (
            db.query(Item)
            .filter(Item.assigned_to_id == current_user.id)
            .order_by(Item.id)
            .all()
        )
        return [_to_item_detail(item, current_user) for item in items]

    @app.get("/items/{item_id}", response_model=ItemDetailOut)
    def get_item(
        item: Item = Depends(deps.get_owned_item),
        current_user: User = Depends(deps.get_current_user),
    ) -> ItemDetailOut:
        return _to_item_detail(item, current_user)

    @app.post("/items/{item_id}/label", response_model=LabelOut)
    def submit_label(
        label_in: LabelIn,
        item: Item = Depends(deps.get_owned_item),
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(deps.get_db),
    ) -> Label:
        """Create or update this reviewer's label for `item` - mirrors
        demos/labeling-django/labeling/views.py's label_item(): look for
        an existing Label first so relabeling updates it in place
        instead of violating models.py's
        UniqueConstraint("item_id", "reviewer_id").
        """
        existing = (
            db.query(Label)
            .filter(Label.item_id == item.id, Label.reviewer_id == current_user.id)
            .first()
        )
        if existing is not None:
            existing.decision = label_in.decision
            existing.corrected_label = label_in.corrected_label
            existing.note = label_in.note
            label = existing
        else:
            label = Label(
                item_id=item.id,
                reviewer_id=current_user.id,
                decision=label_in.decision,
                corrected_label=label_in.corrected_label,
                note=label_in.note,
            )
            db.add(label)

        db.commit()
        db.refresh(label)
        return label

    @app.get("/admin/labels", response_model=list[AdminLabelOut])
    def list_all_labels(
        _admin: User = Depends(deps.require_admin),
        db: Session = Depends(deps.get_db),
    ) -> list[AdminLabelOut]:
        """Every reviewer's labels - the hand-built equivalent of
        opening demos/labeling-django/labeling/admin.py's LabelAdmin at
        /admin/. Nothing like list_display/list_filter/search_fields
        comes free here: this route, and any filtering or pagination it
        might eventually need, is code this demo has to write and
        maintain itself.
        """
        labels = db.query(Label).all()
        return [
            AdminLabelOut(
                id=label.id,
                decision=label.decision,
                corrected_label=label.corrected_label,
                note=label.note,
                created_at=label.created_at,
                reviewer_username=label.reviewer.username,
                item_id=label.item_id,
            )
            for label in labels
        ]

    return app


# Module-level, not just inside __main__ - see
# rest-apis-flask/library-crud/app.py for why: a production ASGI server
# imports this module and looks for `app` directly.
app = create_app()
