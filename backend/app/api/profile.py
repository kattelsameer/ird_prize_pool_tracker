from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_db
from app.models.profile import ConsumerProfile
from app.repositories.profile_repo import update_profile
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=ProfileRead)
def read_profile(profile: ConsumerProfile = Depends(get_current_profile)) -> ConsumerProfile:
    return profile


@router.put("", response_model=ProfileRead)
def update_profile_endpoint(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
) -> ConsumerProfile:
    return update_profile(db, profile, payload.display_name)
