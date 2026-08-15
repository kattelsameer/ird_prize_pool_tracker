"""Password hashing and JWT helpers for authentication.

Kept deliberately small and dependency-light (bcrypt + PyJWT directly, no
auth framework) to match the rest of this codebase's "no complexity for its
own sake" principle -- this app needs login, not a full IdP.
"""
from __future__ import annotations

from datetime import timedelta

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.timeutil import now_kathmandu

_BCRYPT_MAX_PASSWORD_BYTES = 72  # bcrypt silently truncates beyond this; reject instead


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > _BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(f"Password must be at most {_BCRYPT_MAX_PASSWORD_BYTES} bytes")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed hash (shouldn't happen from our own storage) -- fail closed.
        return False


def create_access_token(*, user_id: str) -> str:
    settings = get_settings()
    now = now_kathmandu()
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Returns the user_id (subject) if the token is valid and unexpired, else None.
    Never raises -- callers treat any failure as "not authenticated" (fail closed).
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
