"""Personal-data export bundle (CLAUDE.md §10d: consumers can view/export
their own data). Deliberately excludes notifications and government prize-pool
records -- notifications are application-derived, not user-entered data, and
prize-pool records are public government data, not personal to any one user.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.coupon import CouponRead
from app.schemas.profile import ProfileRead


class AccountExport(BaseModel):
    exported_at: datetime
    account_email: str
    profile: ProfileRead
    coupons: list[CouponRead]
