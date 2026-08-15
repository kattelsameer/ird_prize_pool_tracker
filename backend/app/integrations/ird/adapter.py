"""Adapter: raw IRD API JSON -> internal normalized dataclasses (CLAUDE.md §67).

Nothing outside this package should ever see the raw IRD response shape. Every
consumer (sync service, repositories) works with `NormalizedWinnerRecord`
instances produced here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from app.domain.normalization import normalize_coupon_code


class IrdResponseValidationError(ValueError):
    """Raised when the IRD response is missing required fields or malformed."""


@dataclass(frozen=True)
class NormalizedWinnerRecord:
    source_record_id: str  # f"{draw_id}:{prize_coupon_number}"
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
    normalized_coupon_code: str
    raw_draw_json: dict[str, Any]


@dataclass(frozen=True)
class NormalizedSyncPage:
    limit: int
    offset: int
    total_draws: int | None
    has_more: bool
    winners: list[NormalizedWinnerRecord] = field(default_factory=list)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise IrdResponseValidationError(f"Invalid date value: {value!r}") from exc


def _parse_datetime(value: str | None, *, field_name: str) -> datetime:
    if not value:
        raise IrdResponseValidationError(f"Missing required datetime field: {field_name}")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise IrdResponseValidationError(
            f"Invalid datetime value for {field_name}: {value!r}"
        ) from exc


def adapt_winners_response(payload: dict[str, Any]) -> NormalizedSyncPage:
    """Convert one page of the `/api/v1/public/winners` response into normalized
    records. Raises IrdResponseValidationError on structurally invalid input;
    callers (the sync service) are responsible for catching this and recording
    a failed SyncRun without touching existing data (CLAUDE.md §68).
    """
    if not isinstance(payload, dict):
        raise IrdResponseValidationError("Top-level response is not a JSON object")

    try:
        limit = int(payload["limit"])
        offset = int(payload["offset"])
        has_more = bool(payload["has_more"])
    except (KeyError, TypeError, ValueError) as exc:
        raise IrdResponseValidationError(f"Missing/invalid pagination fields: {exc}") from exc

    total_draws = payload.get("total_draws")
    draws = payload.get("draws")
    if draws is None:
        raise IrdResponseValidationError("Missing 'draws' field")
    if not isinstance(draws, list):
        raise IrdResponseValidationError("'draws' field is not a list")

    winners: list[NormalizedWinnerRecord] = []
    for draw in draws:
        if not isinstance(draw, dict):
            raise IrdResponseValidationError("Draw entry is not a JSON object")
        draw_id = draw.get("draw_id")
        if not draw_id:
            raise IrdResponseValidationError("Draw entry missing draw_id")

        published_at = _parse_datetime(draw.get("published_at"), field_name="published_at")
        claim_deadline = _parse_datetime(draw.get("claim_deadline"), field_name="claim_deadline")
        eligible_from = _parse_date(draw.get("eligible_from"))
        eligible_to = _parse_date(draw.get("eligible_to"))
        claim_open = bool(draw.get("claim_open", False))

        draw_winners = draw.get("winners") or []
        if not isinstance(draw_winners, list):
            raise IrdResponseValidationError(f"Draw {draw_id} 'winners' is not a list")

        for winner in draw_winners:
            if not isinstance(winner, dict):
                raise IrdResponseValidationError(f"Draw {draw_id} has a malformed winner entry")
            coupon_number = winner.get("prize_coupon_number")
            fiscal_year_code = winner.get("prize_fiscal_year_code")
            if not coupon_number or not fiscal_year_code:
                # Missing required identifying fields on an individual winner:
                # skip this one winner (record-level partial-data tolerance)
                # rather than failing the whole page (CLAUDE.md §10e: "treat as
                # partial sync"). The sync service counts this as a skip.
                continue
            try:
                winner_rank = int(winner.get("winner_rank"))
            except (TypeError, ValueError):
                continue

            normalized_code = normalize_coupon_code(coupon_number)
            winners.append(
                NormalizedWinnerRecord(
                    source_record_id=f"{draw_id}:{coupon_number}",
                    draw_id=draw_id,
                    category_title_en=draw.get("category_title_en"),
                    category_title_ne=draw.get("category_title_ne"),
                    draw_type=draw.get("draw_type"),
                    draw_title_en=draw.get("title_en"),
                    draw_title_ne=draw.get("title_ne"),
                    eligible_from=eligible_from,
                    eligible_to=eligible_to,
                    published_at=published_at,
                    claim_deadline=claim_deadline,
                    claim_open=claim_open,
                    winner_rank=winner_rank,
                    prize_fiscal_year_code=fiscal_year_code,
                    prize_coupon_number=coupon_number,
                    normalized_coupon_code=normalized_code,
                    raw_draw_json=draw,
                )
            )

    return NormalizedSyncPage(
        limit=limit,
        offset=offset,
        total_draws=total_draws,
        has_more=has_more,
        winners=winners,
    )
