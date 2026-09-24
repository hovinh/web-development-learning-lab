"""Password hashing and JWT mint/verify - the OAuth2-password + JWT
pattern from FastAPI's own docs (https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/).

This whole file is the blog's "auth is hand-built" claim made concrete:
demos/labeling-django/ gets login/logout/password-hashing from
django.contrib.auth with zero lines like these. Count them if you want
the honest number - this module plus deps.py's get_current_user() is
what a Django project gets by installing `django.contrib.auth` (already
in INSTALLED_APPS by default) and writing zero of its own code.
"""

from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

# Local-dev-only secret, the same spirit as Django's own generated
# `SECRET_KEY = 'django-insecure-...'` (see
# demos/labeling-django/django_project/settings.py) - never a real
# secret, never used outside this demo's own machine.
SECRET_KEY = "demo-only-secret-do-not-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# PasswordHash.recommended() currently means Argon2 (see
# requirements.in's pwdlib[argon2] comment) - FastAPI's docs recommend
# pwdlib over passlib (unmaintained since 2020) for new projects.
password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(username: str) -> str:
    """Mint a JWT whose `sub` (subject) claim is the username, expiring
    ACCESS_TOKEN_EXPIRE_MINUTES from now. Verified by decode_access_token()
    below, called from every authenticated request via deps.py's
    get_current_user().
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Return the username encoded in a valid, unexpired token, or None
    if the token is malformed, tampered with, or expired. jwt.decode()
    raises PyJWTError for all of those - caught here so callers only
    have to handle "valid" vs "not valid", not each specific failure mode.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
