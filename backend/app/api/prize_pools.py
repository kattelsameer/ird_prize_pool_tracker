from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.domain.normalization import normalize_coupon_code
from app.repositories.prize_pool_repo import get_winner, list_winners
from app.schemas.common import Page
from app.schemas.prize_pool import PrizePoolWinnerRead

router = APIRouter(prefix="/api/prize-pools", tags=["prize-pools"])


@router.get("", response_model=Page[PrizePoolWinnerRead])
def list_prize_pools_endpoint(
    fiscal_year: str | None = Query(default=None),
    category: str | None = Query(default=None),
    coupon_code: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    claim_open: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    normalized_code = normalize_coupon_code(coupon_code) if coupon_code else None
    items, total = list_winners(
        db,
        fiscal_year=fiscal_year,
        category=category,
        coupon_code_normalized=normalized_code,
        date_from=date_from,
        date_to=date_to,
        claim_open=claim_open,
        limit=limit,
        offset=offset,
    )
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{winner_id}", response_model=PrizePoolWinnerRead)
def get_prize_pool_endpoint(winner_id: str, db: Session = Depends(get_db)):
    winner = get_winner(db, winner_id)
    if winner is None:
        raise HTTPException(status_code=404, detail="Prize pool record not found")
    return winner
