"""Account-level data rights: export and deletion (CLAUDE.md §10d).

Consumers must be able to view, export, and delete their own personal data.
Viewing is already covered by the existing GET endpoints (profile, coupons);
this module adds the export bundle and the cascading account deletion that
those endpoints don't provide on their own.

Deletion order matters: children before parents, ending with the User row
itself, all inside one transaction so a failure partway through never leaves
an orphaned half-deleted account.
"""
from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.timeutil import now_kathmandu
from app.models.coupon import Coupon
from app.models.notification import Notification
from app.models.profile import ConsumerProfile
from app.models.settings import AppSettings
from app.models.user import User
from app.repositories.coupon_repo import list_all_coupons_for_matching
from app.schemas.account import AccountExport
from app.schemas.coupon import CouponRead
from app.schemas.profile import ProfileRead


def build_account_export(db: Session, user: User, profile: ConsumerProfile) -> AccountExport:
    coupons = list_all_coupons_for_matching(db, profile.id)
    return AccountExport(
        exported_at=now_kathmandu(),
        account_email=user.email,
        profile=ProfileRead.model_validate(profile),
        coupons=[CouponRead.model_validate(c) for c in coupons],
    )


def delete_account(db: Session, user: User, profile: ConsumerProfile) -> None:
    db.execute(delete(Notification).where(Notification.profile_id == profile.id))
    db.execute(delete(Coupon).where(Coupon.profile_id == profile.id))
    db.execute(delete(AppSettings).where(AppSettings.profile_id == profile.id))
    db.execute(delete(ConsumerProfile).where(ConsumerProfile.id == profile.id))
    db.execute(delete(User).where(User.id == user.id))
    db.commit()
