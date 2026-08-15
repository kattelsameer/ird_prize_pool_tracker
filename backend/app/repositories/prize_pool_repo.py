from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.timeutil import now_kathmandu
from app.domain.claim_status import EXPIRING_THRESHOLD
from app.integrations.ird.adapter import NormalizedWinnerRecord
from app.models.prize_pool import PrizePoolWinner

_SORT_COLUMNS = {
    "published_at": PrizePoolWinner.published_at,
    "coupon_code": PrizePoolWinner.normalized_coupon_code,
    "claim_deadline": PrizePoolWinner.claim_deadline,
}


def upsert_winner(
    db: Session, record: NormalizedWinnerRecord, *, source_sync_id: str, source: str = "ird_live"
) -> tuple[PrizePoolWinner, bool]:
    """Upsert one winner keyed on (draw_id, prize_coupon_number).

    Returns (row, was_inserted). Never deletes existing rows; a repeat of an
    already-seen (draw_id, prize_coupon_number) pair updates mutable fields
    only (CLAUDE.md §10e: "unique key... if this combination exists, it's an
    update (or duplicate); if not, it's new").
    """
    existing = db.execute(
        select(PrizePoolWinner).where(
            PrizePoolWinner.draw_id == record.draw_id,
            PrizePoolWinner.prize_coupon_number == record.prize_coupon_number,
        )
    ).scalar_one_or_none()

    if existing is not None:
        existing.claim_open = record.claim_open
        existing.claim_deadline = record.claim_deadline
        existing.published_at = record.published_at
        existing.raw_draw_json = record.raw_draw_json
        existing.source_sync_id = source_sync_id
        db.add(existing)
        return existing, False

    row = PrizePoolWinner(
        source_record_id=record.source_record_id,
        draw_id=record.draw_id,
        category_title_en=record.category_title_en,
        category_title_ne=record.category_title_ne,
        draw_type=record.draw_type,
        draw_title_en=record.draw_title_en,
        draw_title_ne=record.draw_title_ne,
        eligible_from=record.eligible_from,
        eligible_to=record.eligible_to,
        published_at=record.published_at,
        claim_deadline=record.claim_deadline,
        claim_open=record.claim_open,
        winner_rank=record.winner_rank,
        prize_fiscal_year_code=record.prize_fiscal_year_code,
        prize_coupon_number=record.prize_coupon_number,
        normalized_coupon_code=record.normalized_coupon_code,
        raw_draw_json=record.raw_draw_json,
        source=source,
        source_sync_id=source_sync_id,
    )
    db.add(row)
    return row, True


def list_winners(
    db: Session,
    *,
    fiscal_year: str | None = None,
    category: str | None = None,
    coupon_code_normalized: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    claim_open: bool | None = None,
    claim_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "-published_at",
) -> tuple[list[PrizePoolWinner], int]:
    """`claim_status` filters by the same derived CLAIM_ACTIVE/CLAIM_EXPIRING/
    CLAIM_EXPIRED states as app.domain.claim_status.compute_claim_status --
    reusing its EXPIRING_THRESHOLD constant so the two never drift apart.
    Unlike claim_open (a stored column), claim_status is derived from "now",
    so it's expressed here as a boundary comparison against claim_deadline
    rather than a stored value.

    `sort` is `<field>` (ascending) or `-<field>` (descending); `field` is one
    of _SORT_COLUMNS' keys, defaulting to published_at (descending) for an
    unrecognized/empty value.
    """
    stmt = select(PrizePoolWinner)
    if fiscal_year:
        stmt = stmt.where(PrizePoolWinner.prize_fiscal_year_code == fiscal_year)
    if category:
        stmt = stmt.where(PrizePoolWinner.category_title_en == category)
    if coupon_code_normalized:
        stmt = stmt.where(PrizePoolWinner.normalized_coupon_code == coupon_code_normalized)
    if date_from:
        stmt = stmt.where(PrizePoolWinner.eligible_from >= date_from)
    if date_to:
        stmt = stmt.where(PrizePoolWinner.eligible_to <= date_to)
    if claim_open is not None:
        stmt = stmt.where(PrizePoolWinner.claim_open == claim_open)
    if claim_status:
        now = now_kathmandu()
        expiring_boundary = now + EXPIRING_THRESHOLD
        if claim_status == "CLAIM_EXPIRED":
            stmt = stmt.where(
                or_(PrizePoolWinner.claim_deadline <= now, PrizePoolWinner.claim_open.is_(False))
            )
        elif claim_status == "CLAIM_EXPIRING":
            stmt = stmt.where(
                PrizePoolWinner.claim_open.is_(True),
                PrizePoolWinner.claim_deadline > now,
                PrizePoolWinner.claim_deadline < expiring_boundary,
            )
        elif claim_status == "CLAIM_ACTIVE":
            stmt = stmt.where(
                PrizePoolWinner.claim_open.is_(True),
                PrizePoolWinner.claim_deadline >= expiring_boundary,
            )

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    field = sort[1:] if sort.startswith("-") else sort
    column = _SORT_COLUMNS.get(field, PrizePoolWinner.published_at)
    # Unrecognized/empty field falls back to published_at descending (the default view).
    descending = sort.startswith("-") or field not in _SORT_COLUMNS
    order_col = column.desc() if descending else column.asc()

    stmt = stmt.order_by(order_col).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def get_winner(db: Session, winner_id: str) -> PrizePoolWinner | None:
    return db.execute(select(PrizePoolWinner).where(PrizePoolWinner.id == winner_id)).scalar_one_or_none()


def list_all_winners(db: Session) -> list[PrizePoolWinner]:
    return list(db.execute(select(PrizePoolWinner)).scalars().all())
