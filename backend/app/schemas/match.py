from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.domain.claim_status import ClaimStatus


class MatchRead(BaseModel):
    """Application-derived information (CLAUDE.md §6). Language here must say
    'matches published data', never 'guaranteed prize' (CLAUDE.md §65).

    `prize_amount`/`prize_amount_net` are the two known, fixed published tiers
    (CLAUDE.md §10a) looked up by category -- null if IRD ever publishes a
    category outside that table, never a guessed amount (CLAUDE.md §5)."""

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
    prize_amount: int | None
    prize_amount_net: int | None
    eligible_from: date | None
    eligible_to: date | None
    message: str
