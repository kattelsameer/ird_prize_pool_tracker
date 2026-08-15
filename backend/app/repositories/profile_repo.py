from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import ConsumerProfile


def get_or_create_default_profile(db: Session) -> ConsumerProfile:
    """This is a local, single-user application (CLAUDE.md §23: 'keep it
    local/simple rather than introducing unnecessary authentication
    infrastructure'). We always operate against one default profile row,
    created lazily on first access, while keeping the schema shaped so real
    multi-profile auth could be added later without a rewrite.
    """
    profile = db.execute(select(ConsumerProfile).limit(1)).scalar_one_or_none()
    if profile is None:
        profile = ConsumerProfile(display_name=None)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def update_profile(db: Session, profile: ConsumerProfile, display_name: str | None) -> ConsumerProfile:
    profile.display_name = display_name
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile
