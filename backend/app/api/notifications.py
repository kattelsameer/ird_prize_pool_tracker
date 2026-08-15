from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_db
from app.models.profile import ConsumerProfile
from app.repositories.notification_repo import (
    get_notification,
    list_notifications,
    mark_all_read,
    mark_read,
)
from app.schemas.common import Page
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=Page[NotificationRead])
def list_notifications_endpoint(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    items, total = list_notifications(
        db, profile.id, unread_only=unread_only, limit=limit, offset=offset
    )
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read_endpoint(
    notification_id: str,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    notification = get_notification(db, profile.id, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return mark_read(db, notification)


@router.post("/read-all")
def mark_all_notifications_read_endpoint(
    db: Session = Depends(get_db), profile: ConsumerProfile = Depends(get_current_profile)
):
    count = mark_all_read(db, profile.id)
    return {"marked_read": count}
