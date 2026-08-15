from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.profile import ConsumerProfile
from app.models.user import User
from app.repositories.profile_repo import get_or_create_profile_for_user
from app.repositories.user_repo import get_user_by_id

__all__ = ["get_db", "get_current_user", "get_current_profile"]

# auto_error=False so we can raise our own 401 with a consistent, user-safe
# detail message rather than FastAPI's default "Not authenticated".
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolves the authenticated user from a `Authorization: Bearer <token>`
    header. Fails closed on any problem (missing header, malformed/expired
    token, deleted user) with a single generic 401 -- never distinguishes the
    failure reason to the client, to avoid leaking account-enumeration signals.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise unauthorized

    user = get_user_by_id(db, user_id)
    if user is None:
        raise unauthorized

    return user


def get_current_profile(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> ConsumerProfile:
    """Every route that operates on "my coupons"/"my notifications"/etc. depends
    on this, not on get_current_user directly, so route handlers never need to
    know about the profile-per-user indirection (CLAUDE.md §23).
    """
    return get_or_create_profile_for_user(db, user.id)
