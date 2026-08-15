from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.timeutil import now_kathmandu
from app.models.notification import Notification


def notification_exists(db: Session, dedup_key: str) -> bool:
    return (
        db.execute(select(Notification.id).where(Notification.dedup_key == dedup_key)).scalar_one_or_none()
        is not None
    )


def create_notification_if_new(
    db: Session,
    *,
    profile_id: str,
    type_: str,
    message: str,
    dedup_key: str,
    coupon_id: str | None = None,
    draw_id: str | None = None,
) -> Notification | None:
    """Create a notification unless one with this dedup_key already exists.
    Returns None if it already existed (no duplicate notification created),
    per CLAUDE.md §33: "A synchronization process should not generate the same
    notification repeatedly unless the underlying event has genuinely changed."
    """
    if notification_exists(db, dedup_key):
        return None
    notification = Notification(
        profile_id=profile_id,
        type=type_,
        coupon_id=coupon_id,
        draw_id=draw_id,
        message=message,
        dedup_key=dedup_key,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(
    db: Session, profile_id: str, *, unread_only: bool = False, limit: int = 50, offset: int = 0
) -> tuple[list[Notification], int]:
    stmt = select(Notification).where(Notification.profile_id == profile_id)
    if unread_only:
        stmt = stmt.where(Notification.read_at.is_(None))
    total = len(db.execute(stmt).scalars().all())
    stmt = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def mark_read(db: Session, notification: Notification) -> Notification:
    notification.read_at = now_kathmandu()
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, profile_id: str) -> int:
    stmt = select(Notification).where(
        Notification.profile_id == profile_id, Notification.read_at.is_(None)
    )
    unread = list(db.execute(stmt).scalars().all())
    now = now_kathmandu()
    for n in unread:
        n.read_at = now
        db.add(n)
    db.commit()
    return len(unread)


def get_notification(db: Session, profile_id: str, notification_id: str) -> Notification | None:
    return db.execute(
        select(Notification).where(
            Notification.id == notification_id, Notification.profile_id == profile_id
        )
    ).scalar_one_or_none()
