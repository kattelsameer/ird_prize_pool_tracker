"""Derives which draw period governs a coupon's transaction date, using only
*synced* prize-pool data (CLAUDE.md §66/§67) -- and, only when no synced draw
yet covers that date, an *estimated* still-open period from the real Nepal
1st/16th BS cadence (CLAUDE.md §10a/§10b).

This is additive to (not a replacement for) `app.domain.matching`: it answers
"what draw window covers this date, and has it been drawn yet", independent
of whether the coupon's code actually won. Estimates are always flagged
`is_estimated=True` -- application-derived information, never an
IRD-published fact (CLAUDE.md §6/§65). This never invents a draw *result*,
only a period boundary and an expected publish date.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.nepali_calendar import bs_half_month_period_for_date


@dataclass(frozen=True)
class KnownDrawPeriod:
    """One distinct synced draw window (deduped by draw_id)."""

    draw_id: str
    draw_title_en: str | None
    eligible_from: date
    eligible_to: date
    published_at: datetime


@dataclass(frozen=True)
class DrawPeriodStatus:
    """Per-coupon, application-derived context about which draw period its
    transaction date falls into.

    state:
      DRAWN   -- a synced draw's eligible window contains the transaction
                 date; that draw has been published (pair with GET
                 /api/matches to see whether this coupon actually won it).
      PENDING -- no synced draw covers this date yet, and it falls after the
                 newest draw we've synced -- the covering period is likely
                 still open. `eligible_from`/`eligible_to`/
                 `estimated_publish_date` are estimated from the regular
                 1st/16th cadence, flagged `is_estimated=True`.
      UNKNOWN -- no synced draw covers this date, but it's not newer than our
                 latest synced draw either -- most likely a sync gap, not "no
                 draw yet". No period is guessed in this case.
    """

    state: str
    eligible_from: date | None
    eligible_to: date | None
    draw_id: str | None
    draw_title_en: str | None
    published_at: datetime | None
    estimated_publish_date: date | None
    is_estimated: bool


def classify_period(
    transaction_date: date | None,
    known_periods: list[KnownDrawPeriod],
) -> DrawPeriodStatus | None:
    """Classify which draw period governs `transaction_date`.

    Returns None if `transaction_date` is unset -- nothing to classify.
    """
    if transaction_date is None:
        return None

    for period in known_periods:
        if period.eligible_from <= transaction_date <= period.eligible_to:
            return DrawPeriodStatus(
                state="DRAWN",
                eligible_from=period.eligible_from,
                eligible_to=period.eligible_to,
                draw_id=period.draw_id,
                draw_title_en=period.draw_title_en,
                published_at=period.published_at,
                estimated_publish_date=None,
                is_estimated=False,
            )

    latest_known_eligible_to = max((p.eligible_to for p in known_periods), default=None)
    if latest_known_eligible_to is not None and transaction_date <= latest_known_eligible_to:
        return DrawPeriodStatus(
            state="UNKNOWN",
            eligible_from=None,
            eligible_to=None,
            draw_id=None,
            draw_title_en=None,
            published_at=None,
            estimated_publish_date=None,
            is_estimated=False,
        )

    estimated = bs_half_month_period_for_date(transaction_date)
    return DrawPeriodStatus(
        state="PENDING",
        eligible_from=estimated.period_start,
        eligible_to=estimated.period_end,
        draw_id=None,
        draw_title_en=None,
        published_at=None,
        estimated_publish_date=estimated.expected_publish_date,
        is_estimated=True,
    )
