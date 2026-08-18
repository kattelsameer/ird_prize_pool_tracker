"""Pure coupon <-> prize-pool matching algorithm (CLAUDE.md §29-30, §50, §10e).

This module has zero dependency on SQLAlchemy/FastAPI so the core business
rule -- "does this coupon match a published winner?" -- can be unit tested in
any Python environment, independent of whether the ORM/web stack is
installed. `app.services.matching_service` is a thin adapter that loads ORM
rows, converts them to the dataclasses below, calls `match_coupons`, and
converts the results back into persisted/serializable form.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.claim_status import ClaimStatus, compute_claim_status
from app.domain.normalization import normalize_coupon_code, normalize_fiscal_year


@dataclass(frozen=True)
class CouponInput:
    """Minimal view of a user coupon needed for matching."""

    coupon_id: str
    coupon_code: str
    fiscal_year: str | None
    transaction_date: date | None


@dataclass(frozen=True)
class WinnerInput:
    """Minimal view of a normalized PrizePoolWinner row needed for matching."""

    draw_id: str
    prize_coupon_number: str
    prize_fiscal_year_code: str
    eligible_from: date | None
    eligible_to: date | None
    published_at: datetime
    claim_deadline: datetime
    claim_open: bool
    winner_rank: int
    category_title_en: str
    draw_type: str
    draw_title_en: str
    prize_amount: int | None
    prize_amount_net: int | None


@dataclass(frozen=True)
class MatchResult:
    coupon_id: str
    coupon_code: str
    draw_id: str
    prize_coupon_number: str
    fiscal_year_unconfirmed: bool
    eligible_period_warning: bool
    claim_status: ClaimStatus
    winner_rank: int
    category_title_en: str
    draw_type: str
    draw_title_en: str
    claim_deadline: datetime
    claim_open: bool
    prize_amount: int | None
    prize_amount_net: int | None
    eligible_from: date | None
    eligible_to: date | None


def _transaction_outside_eligible_period(
    transaction_date: date | None,
    eligible_from: date | None,
    eligible_to: date | None,
) -> bool:
    """Advisory-only check: does the user's transaction date fall outside the
    winner's published eligible period? This NEVER excludes a coupon-code
    match (CLAUDE.md §29/§10e); it only surfaces a data-quality warning to the
    user, since the coupon code itself is the authoritative winning signal.
    """
    if transaction_date is None or eligible_from is None or eligible_to is None:
        return False
    return not (eligible_from <= transaction_date <= eligible_to)


def match_coupons(
    coupons: list[CouponInput],
    winners: list[WinnerInput],
    *,
    now: datetime,
) -> list[MatchResult]:
    """Match every coupon against every winner.

    A coupon matches a winner when:
      normalize(coupon.coupon_code) == normalize(winner.prize_coupon_number)

    If the coupon has a fiscal_year set and it differs from the winner's
    prize_fiscal_year_code, the match is still returned but flagged
    `fiscal_year_unconfirmed=True` rather than excluded (CLAUDE.md §10e).

    Network is never part of the matching condition (not modeled here at all
    since the confirmed live IRD payload has no network field, CLAUDE.md §G).

    A coupon may match multiple winners; all matches are returned.
    """
    # Index winners by normalized coupon code for O(1) lookup per coupon,
    # tolerating duplicate government records (CLAUDE.md §10e: "store all
    # occurrences") -- duplicates are collapsed upstream at persistence time by
    # the (draw_id, prize_coupon_number) unique key, so by the time winners
    # reach this function there should be no true duplicates, but we don't
    # assume that here and simply iterate all of them.
    index: dict[str, list[WinnerInput]] = {}
    for winner in winners:
        key = normalize_coupon_code(winner.prize_coupon_number)
        index.setdefault(key, []).append(winner)

    results: list[MatchResult] = []
    for coupon in coupons:
        normalized_code = normalize_coupon_code(coupon.coupon_code)
        matching_winners = index.get(normalized_code, [])
        if not matching_winners:
            continue

        normalized_coupon_fy = normalize_fiscal_year(coupon.fiscal_year)

        for winner in matching_winners:
            fiscal_year_unconfirmed = (
                normalized_coupon_fy is not None
                and normalized_coupon_fy != winner.prize_fiscal_year_code
            )
            eligible_period_warning = _transaction_outside_eligible_period(
                coupon.transaction_date, winner.eligible_from, winner.eligible_to
            )
            claim_status = compute_claim_status(
                now=now,
                claim_deadline=winner.claim_deadline,
                claim_open=winner.claim_open,
            )
            results.append(
                MatchResult(
                    coupon_id=coupon.coupon_id,
                    coupon_code=coupon.coupon_code,
                    draw_id=winner.draw_id,
                    prize_coupon_number=winner.prize_coupon_number,
                    fiscal_year_unconfirmed=fiscal_year_unconfirmed,
                    eligible_period_warning=eligible_period_warning,
                    claim_status=claim_status,
                    winner_rank=winner.winner_rank,
                    category_title_en=winner.category_title_en,
                    draw_type=winner.draw_type,
                    draw_title_en=winner.draw_title_en,
                    claim_deadline=winner.claim_deadline,
                    claim_open=winner.claim_open,
                    prize_amount=winner.prize_amount,
                    prize_amount_net=winner.prize_amount_net,
                    eligible_from=winner.eligible_from,
                    eligible_to=winner.eligible_to,
                )
            )
    return results
