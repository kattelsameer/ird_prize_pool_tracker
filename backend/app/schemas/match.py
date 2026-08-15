from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain.claim_status import ClaimStatus


class MatchRead(BaseModel):
    """Application-derived information (CLAUDE.md §6). Language here must say
    'matches published data', never 'guaranteed prize' (CLAUDE.md §65)."""

    coupon_id: str
    coupon_code: str
    draw_id: str
    prize_coupon_number: str
    winner_rank: int
    category_title_en: str | None
    draw_type: str | None
    draw_title_en: str | None
    fiscal_year_unconfirmed: bool
    eligible_period_warning: bool
    claim_status: ClaimStatus
    claim_deadline: datetime
    claim_open: bool
    message: str
