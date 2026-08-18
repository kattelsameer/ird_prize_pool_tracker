"""DB-aware adapter for `app.domain.draw_period` (CLAUDE.md §29-30 sibling
concern). Draws are only ever implicit in this system -- one row per
(draw_id, prize_coupon_number) on `PrizePoolWinner` -- so "known periods"
means: every distinct draw_id we've actually synced, deduped, taking its
eligible window and publish timestamp (CLAUDE.md §66).
"""
from __future__ import annotations

from dataclasses import asdict

from sqlalchemy.orm import Session

from app.domain.draw_period import DrawPeriodStatus, KnownDrawPeriod, classify_period
from app.repositories.coupon_repo import list_all_coupons_for_matching
from app.repositories.prize_pool_repo import list_all_winners


def _known_periods(db: Session) -> list[KnownDrawPeriod]:
    seen: dict[str, KnownDrawPeriod] = {}
    for winner in list_all_winners(db):
        if winner.draw_id in seen or winner.eligible_from is None or winner.eligible_to is None:
            continue
        seen[winner.draw_id] = KnownDrawPeriod(
            draw_id=winner.draw_id,
            draw_title_en=winner.draw_title_en,
            eligible_from=winner.eligible_from,
            eligible_to=winner.eligible_to,
            published_at=winner.published_at,
        )
    return list(seen.values())


def compute_draw_period_statuses_for_profile(db: Session, profile_id: str) -> dict[str, DrawPeriodStatus]:
    """One entry per coupon (keyed by the coupon's id) that has a
    transaction_date set; coupons without one are omitted -- there's nothing
    to classify."""
    known_periods = _known_periods(db)
    statuses: dict[str, DrawPeriodStatus] = {}
    for coupon in list_all_coupons_for_matching(db, profile_id):
        status = classify_period(coupon.transaction_date, known_periods)
        if status is not None:
            statuses[coupon.id] = status
    return statuses


def draw_period_status_to_dict(coupon_id: str, status: DrawPeriodStatus) -> dict:
    return {"coupon_id": coupon_id, **asdict(status)}
