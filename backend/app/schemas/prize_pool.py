from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class PrizePoolWinnerRead(BaseModel):
    """Government-published data, clearly distinct from user/app-derived data
    (CLAUDE.md §6, §10d)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    draw_id: str
    category_title_en: str | None
    category_title_ne: str | None
    draw_type: str | None
    draw_title_en: str | None
    draw_title_ne: str | None
    eligible_from: date | None
    eligible_to: date | None
    published_at: datetime
    claim_deadline: datetime
    claim_open: bool
    winner_rank: int
    prize_fiscal_year_code: str
    prize_coupon_number: str
    source: str
    created_at: datetime
