"""Matching engine service: DB-aware adapter around app.domain.matching
(CLAUDE.md §29-30). Keeps the pure algorithm testable in isolation while this
layer handles loading ORM rows and converting them to/from plain dataclasses.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.timeutil import now_kathmandu
from app.domain.matching import CouponInput, MatchResult, WinnerInput, match_coupons
from app.domain.prize_tiers import prize_amounts_for_category
from app.models.coupon import Coupon
from app.models.prize_pool import PrizePoolWinner
from app.repositories.coupon_repo import list_all_coupons_for_matching
from app.repositories.prize_pool_repo import list_all_winners


def _coupon_to_input(coupon: Coupon) -> CouponInput:
    return CouponInput(
        coupon_id=coupon.id,
        coupon_code=coupon.coupon_code,
        fiscal_year=coupon.fiscal_year,
        transaction_date=coupon.transaction_date,
    )


def _winner_to_input(winner: PrizePoolWinner) -> WinnerInput:
    prize_amount, prize_amount_net = prize_amounts_for_category(winner.category_title_en)
    return WinnerInput(
        draw_id=winner.draw_id,
        prize_coupon_number=winner.prize_coupon_number,
        prize_fiscal_year_code=winner.prize_fiscal_year_code,
        eligible_from=winner.eligible_from,
        eligible_to=winner.eligible_to,
        published_at=winner.published_at,
        claim_deadline=winner.claim_deadline,
        claim_open=winner.claim_open,
        winner_rank=winner.winner_rank,
        category_title_en=winner.category_title_en or "",
        draw_type=winner.draw_type or "",
        draw_title_en=winner.draw_title_en or "",
        prize_amount=prize_amount,
        prize_amount_net=prize_amount_net,
    )


def compute_matches_for_profile(db: Session, profile_id: str) -> list[MatchResult]:
    """Run the matching engine for every coupon belonging to `profile_id`
    against every known winner. This recomputes on demand rather than storing
    match state, so results are always fresh relative to current coupon/winner
    data (no risk of stale cached matches).
    """
    coupons = [_coupon_to_input(c) for c in list_all_coupons_for_matching(db, profile_id)]
    winners = [_winner_to_input(w) for w in list_all_winners(db)]
    return match_coupons(coupons, winners, now=now_kathmandu())


def build_match_message(result: MatchResult) -> str:
    """User-facing copy that carefully distinguishes 'matches published data'
    from 'guaranteed prize' (CLAUDE.md §65)."""
    parts = [
        f"Your coupon matches a result published by IRD for the "
        f"\"{result.draw_title_en or result.category_title_en}\" draw."
    ]
    if result.fiscal_year_unconfirmed:
        parts.append(
            "The fiscal year you entered doesn't match the fiscal year IRD "
            "published for this result -- please double-check before assuming this is your win."
        )
    if result.eligible_period_warning:
        parts.append(
            "Note: the transaction date you entered falls outside the eligible "
            "period IRD published for this draw. Please verify your entry."
        )
    parts.append(
        "To claim, you must provide the original physical bill and PAN in "
        "person at an Inland Revenue Office before the claim deadline."
    )
    return " ".join(parts)
