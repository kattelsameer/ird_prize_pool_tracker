from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.profile import ConsumerProfile
from app.repositories.profile_repo import get_or_create_default_profile

__all__ = ["get_db", "get_current_profile"]


def get_current_profile(db: Session = Depends(get_db)) -> ConsumerProfile:
    """Local, single-user app -- always resolves to the one default profile
    (CLAUDE.md §23). Kept as a separate function so a real auth-based lookup
    can replace this later without touching route handlers.
    """
    return get_or_create_default_profile(db)
