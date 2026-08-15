from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_profile, get_db
from app.models.profile import ConsumerProfile
from app.repositories.coupon_repo import (
    create_coupon,
    delete_coupon,
    get_coupon,
    list_coupons,
    update_coupon,
)
from app.schemas.common import Page
from app.schemas.coupon import CouponCreate, CouponRead, CouponUpdate
from app.services.matching_service import compute_matches_for_profile
from app.services.notification_service import generate_match_and_claim_notifications

router = APIRouter(prefix="/api/coupons", tags=["coupons"])


def _refresh_matches_and_notify(db: Session, profile_id: str) -> None:
    """Re-evaluate matches for this profile and notify on anything newly
    eligible. A coupon added (or edited) *after* a sync already found the
    matching winner would otherwise surface only on the dashboard/wins view
    with no notification -- CLAUDE.md §33 lists "newly eligible coupon" as
    its own notification trigger, distinct from sync-time match discovery.
    `generate_match_and_claim_notifications` dedupes by (coupon_id, draw_id),
    so this never double-notifies if a later sync reprocesses the same match.
    """
    matches = compute_matches_for_profile(db, profile_id)
    generate_match_and_claim_notifications(db, profile_id, matches)


@router.get("", response_model=Page[CouponRead])
def list_coupons_endpoint(
    search: str | None = Query(default=None),
    network: str | None = Query(default=None),
    fiscal_year: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    items, total = list_coupons(
        db,
        profile.id,
        search=search,
        network=network,
        fiscal_year=fiscal_year,
        limit=limit,
        offset=offset,
    )
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=CouponRead, status_code=201)
def create_coupon_endpoint(
    payload: CouponCreate,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    coupon = create_coupon(
        db,
        profile_id=profile.id,
        coupon_code=payload.coupon_code,
        transaction_date=payload.transaction_date,
        fiscal_year=payload.fiscal_year,
        network=payload.network,
    )
    _refresh_matches_and_notify(db, profile.id)
    return coupon


@router.get("/{coupon_id}", response_model=CouponRead)
def get_coupon_endpoint(
    coupon_id: str,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    coupon = get_coupon(db, profile.id, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon


@router.put("/{coupon_id}", response_model=CouponRead)
def update_coupon_endpoint(
    coupon_id: str,
    payload: CouponUpdate,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    coupon = get_coupon(db, profile.id, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    update_kwargs = payload.model_dump(exclude_unset=True)
    updated = update_coupon(
        db,
        coupon,
        coupon_code=update_kwargs.get("coupon_code"),
        transaction_date=update_kwargs.get("transaction_date", ...),
        fiscal_year=update_kwargs.get("fiscal_year", ...),
        network=update_kwargs.get("network", ...),
    )
    _refresh_matches_and_notify(db, profile.id)
    return updated


@router.delete("/{coupon_id}", status_code=204)
def delete_coupon_endpoint(
    coupon_id: str,
    db: Session = Depends(get_db),
    profile: ConsumerProfile = Depends(get_current_profile),
):
    coupon = get_coupon(db, profile.id, coupon_id)
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    delete_coupon(db, coupon)
    return None
