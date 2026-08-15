from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_current_user, get_db
from app.models.profile import ConsumerProfile
from app.models.user import User
from app.repositories.profile_repo import update_profile
from app.schemas.account import AccountExport
from app.schemas.profile import ProfileRead, ProfileUpdate
from app.services.account_service import build_account_export, delete_account

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


@router.get("/export", response_model=AccountExport)
def export_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    profile: ConsumerProfile = Depends(get_current_profile),
) -> AccountExport:
    """Personal-data export (CLAUDE.md §10d): everything the consumer entered
    themselves, in one downloadable JSON bundle.
    """
    return build_account_export(db, user, profile)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    profile: ConsumerProfile = Depends(get_current_profile),
) -> Response:
    """Permanently deletes the account and all associated data (CLAUDE.md
    §10d's "right to deletion"). Irreversible; the frontend must confirm
    before calling this.
    """
    delete_account(db, user, profile)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
