from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.core.timeutil import now_kathmandu
from app.domain.claim_status import ClaimStatus, compute_claim_status
from app.domain.prize_tiers import prize_amounts_for_category
from app.models.prize_pool import PrizePoolWinner


class PrizePoolWinnerRead(BaseModel):
    """Government-published data, clearly distinct from user/app-derived data
    (CLAUDE.md §6, §10d).

    Field names here are the outward-facing API contract, which intentionally
    differs from PrizePoolWinner's column names (e.g. `category` here vs.
    `category_title_en` on the model, which itself mirrors IRD's own field
    name) -- this schema is the adapter boundary CLAUDE.md §67 calls for, so a
    future IRD field rename only has to be reconciled in `from_model` below,
    not in every frontend component. Use `from_model`, not `model_validate`
    directly, since `claim_status` and the prize amounts are derived rather
    than stored columns.
    """

    id: str
    source_record_id: str
    draw_id: str
    draw_title_en: str | None
    draw_title_np: str | None
    category: str | None
    prize_amount: int | None
    prize_amount_net: int | None
    coupon_code: str
    normalized_coupon_code: str
    fiscal_year: str
    network: str | None  # IRD's public API does not publish network/provider per winner record
    eligible_from: date | None
    eligible_to: date | None
    published_at: datetime
    claim_deadline: datetime
    claim_open: bool
    claim_status: ClaimStatus
    source: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, winner: PrizePoolWinner) -> "PrizePoolWinnerRead":
        amount, amount_net = prize_amounts_for_category(winner.category_title_en)
        return cls(
            id=winner.id,
            source_record_id=winner.source_record_id,
            draw_id=winner.draw_id,
            draw_title_en=winner.draw_title_en,
            draw_title_np=winner.draw_title_ne,
            category=winner.category_title_en,
            prize_amount=amount,
            prize_amount_net=amount_net,
            coupon_code=winner.prize_coupon_number,
            normalized_coupon_code=winner.normalized_coupon_code,
            fiscal_year=winner.prize_fiscal_year_code,
            network=None,
            eligible_from=winner.eligible_from,
            eligible_to=winner.eligible_to,
            published_at=winner.published_at,
            claim_deadline=winner.claim_deadline,
            claim_open=winner.claim_open,
            claim_status=compute_claim_status(
                now=now_kathmandu(), claim_deadline=winner.claim_deadline, claim_open=winner.claim_open
            ),
            source=winner.source,
            created_at=winner.created_at,
            updated_at=winner.updated_at,
        )
