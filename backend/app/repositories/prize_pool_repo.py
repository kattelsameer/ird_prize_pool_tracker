from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.integrations.ird.adapter import NormalizedWinnerRecord
from app.models.prize_pool import PrizePoolWinner


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
    limit: int = 50,
    offset: int = 0,
    sort_desc: bool = True,
) -> tuple[list[PrizePoolWinner], int]:
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

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    order_col = PrizePoolWinner.published_at.desc() if sort_desc else PrizePoolWinner.published_at.asc()
    stmt = stmt.order_by(order_col).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def get_winner(db: Session, winner_id: str) -> PrizePoolWinner | None:
    return db.execute(select(PrizePoolWinner).where(PrizePoolWinner.id == winner_id)).scalar_one_or_none()


def list_all_winners(db: Session) -> list[PrizePoolWinner]:
    return list(db.execute(select(PrizePoolWinner)).scalars().all())
