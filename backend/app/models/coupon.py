"""Coupon model (CLAUDE.md §24-26)."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, ForeignKey, String

from app.models.types import TZDateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutil import now_kathmandu
from app.models.base import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("consumer_profiles.id"), nullable=False, index=True
    )

    # Generated as f"{fiscal_year}-{normalized_coupon_code}" when fiscal_year is
    # known, else f"UNSPECIFIED-{normalized_coupon_code}" (CLAUDE.md §25). Not
    # globally unique on its own (the same coupon may legitimately be entered
    # more than once via the dual digital/manual pathways, CLAUDE.md §10a) so
    # this is indexed but not a primary/unique key.
    coupon_id: Mapped[str] = mapped_column(String(160), index=True, nullable=False)

    coupon_code: Mapped[str] = mapped_column(String(64), nullable=False)
    normalized_coupon_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    fiscal_year: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    network: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(TZDateTime(), default=now_kathmandu)
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime(), default=now_kathmandu, onupdate=now_kathmandu
    )
