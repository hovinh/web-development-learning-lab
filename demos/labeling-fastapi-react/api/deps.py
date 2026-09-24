"""Shared FastAPI dependencies: a DB session per request, the current
authenticated user, an admin-only gate, and the one shared ownership
check.

Compare demos/labeling-django/labeling/views.py: Django's equivalent of
get_current_user is @login_required (one decorator, from a framework
that already knows how to look up "who's making this request" from a
session cookie); the equivalent of get_owned_item is
get_object_or_404(Item, pk=item_id, assigned_to=request.user) written
inline in the one view that needs it. Here, both are their own
functions specifically so more than one route can reuse them - see
main.py's docstring for exactly how many routes depend on each, and
README.md's "Ownership: a dependency, not a queryset" section for why
that's still not the same guarantee as Django's.
"""

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Item, User
from security import decode_access_token

# tokenUrl is where a client (or FastAPI's own /docs Swagger UI - see
# README.md's "Manual checks") goes to exchange a username/password for
# a token; it doesn't route the request there itself.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db() -> Generator[Session, None, None]:
    """One session per request, closed when the request finishes.

    A plain function, not a context manager class, because FastAPI's
    dependency system runs everything after the `yield` as cleanup
    automatically - this is FastAPI's own documented pattern for a
    per-request DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Every authenticated route depends on this (directly or via
    require_admin/get_owned_item below) - it's this demo's replacement
    for Django's session-cookie-based request.user, rebuilt from a JWT
    on every single request instead of being looked up once by
    middleware.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    username = decode_access_token(token)
    if username is None:
        raise credentials_error

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_error

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Gates main.py's /admin/* routes - the hand-built equivalent of
    Django's is_staff check, which the Django admin site already
    performs for every view registered in labeling/admin.py.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_owned_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Item:
    """The one shared ownership check, per the web-stack-advisor skill's
    rule ("put the ownership filter in one place"): look up `item_id`
    and 404 unless it's assigned to the requesting user.

    Sharing this function doesn't make it automatic, though - every
    route that needs the guarantee still has to remember to add
    `Depends(get_owned_item)` itself (see main.py's GET /items/{item_id}
    and POST /items/{item_id}/label). A route that forgot it would
    compile and run fine, silently returning or modifying rows that
    aren't the caller's - nothing in FastAPI enforces that every
    item-scoped route uses this dependency, the way Django's
    Item.objects.filter(assigned_to=request.user) makes the unfiltered
    query awkward to even write by accident.
    """
    item = (
        db.query(Item)
        .filter(Item.id == item_id, Item.assigned_to_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item
