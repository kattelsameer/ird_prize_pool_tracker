"""Normalized government prize-pool winner model (CLAUDE.md §27, §66).

One row per (draw_id, prize_coupon_number) -- the unique key IRD-side sync
upserts against (CLAUDE.md §10e "unique key is (prize_coupon_number,
draw_id)"). Both the normalized fields AND the full raw draw JSON payload are
stored for traceability (CLAUDE.md §66).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, Integer, JSON, String, UniqueConstraint

from app.models.types import TZDateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.timeutil import now_kathmandu
from app.models.base import Base


class PrizePoolWinner(Base):
    __tablename__ = "prize_pool_winners"
    __table_args__ = (
        UniqueConstraint("draw_id", "prize_coupon_number", name="uq_draw_coupon"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_record_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    draw_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    category_title_en: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category_title_ne: Mapped[str | None] = mapped_column(String(200), nullable=True)
    draw_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    draw_title_en: Mapped[str | None] = mapped_column(String(400), nullable=True)
    draw_title_ne: Mapped[str | None] = mapped_column(String(400), nullable=True)

    eligible_from: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    eligible_to: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    published_at: Mapped[datetime] = mapped_column(TZDateTime(), nullable=False)
    claim_deadline: Mapped[datetime] = mapped_column(TZDateTime(), nullable=False, index=True)
    claim_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    winner_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    prize_fiscal_year_code: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    prize_coupon_number: Mapped[str] = mapped_column(String(64), nullable=False)
    normalized_coupon_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    raw_draw_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    source: Mapped[str] = mapped_column(String(20), nullable=False, default="ird_live", index=True)
    source_sync_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("sync_runs.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(TZDateTime(), default=now_kathmandu)
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime(), default=now_kathmandu, onupdate=now_kathmandu
    )
