from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import ConsumerProfile


def get_or_create_profile_for_user(db: Session, user_id: str) -> ConsumerProfile:
    """One profile per authenticated user (CLAUDE.md §23), created lazily on
    first access after registration/login rather than at registration time --
    keeps registration itself minimal (just the account).
    """
    profile = db.execute(
        select(ConsumerProfile).where(ConsumerProfile.user_id == user_id)
    ).scalar_one_or_none()
    if profile is None:
        profile = ConsumerProfile(user_id=user_id, display_name=None)
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


def list_all_profiles(db: Session) -> list[ConsumerProfile]:
    """Every registered user's profile -- used by the sync job, which must
    refresh matches/notifications for all users, not just one implicit
    profile, now that the app supports real multi-user accounts.
    """
    return list(db.execute(select(ConsumerProfile)).scalars().all())
