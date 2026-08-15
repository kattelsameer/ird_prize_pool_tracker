from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.normalization import normalize_coupon_code, normalize_fiscal_year, normalize_network_name
from app.models.coupon import Coupon


def _build_coupon_id(fiscal_year: str | None, normalized_code: str) -> str:
    prefix = fiscal_year if fiscal_year else "UNSPECIFIED"
    return f"{prefix}-{normalized_code}"


def create_coupon(
    db: Session,
    *,
    profile_id: str,
    coupon_code: str,
    transaction_date: date | None,
    fiscal_year: str | None,
    network: str | None,
) -> Coupon:
    normalized_fy = normalize_fiscal_year(fiscal_year)
    normalized_code = normalize_coupon_code(coupon_code)
    coupon = Coupon(
        profile_id=profile_id,
        coupon_id=_build_coupon_id(normalized_fy, normalized_code),
        coupon_code=coupon_code,
        normalized_coupon_code=normalized_code,
        transaction_date=transaction_date,
        fiscal_year=normalized_fy,
        network=normalize_network_name(network),
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def update_coupon(
    db: Session,
    coupon: Coupon,
    *,
    coupon_code: str | None,
    transaction_date: date | None | object = ...,
    fiscal_year: str | None | object = ...,
    network: str | None | object = ...,
) -> Coupon:
    if coupon_code is not None:
        coupon.coupon_code = coupon_code
        coupon.normalized_coupon_code = normalize_coupon_code(coupon_code)
    if fiscal_year is not ...:
        coupon.fiscal_year = normalize_fiscal_year(fiscal_year)
    if transaction_date is not ...:
        coupon.transaction_date = transaction_date
    if network is not ...:
        coupon.network = normalize_network_name(network)
    coupon.coupon_id = _build_coupon_id(coupon.fiscal_year, coupon.normalized_coupon_code)
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    return coupon


def get_coupon(db: Session, profile_id: str, coupon_pk: str) -> Coupon | None:
    return db.execute(
        select(Coupon).where(Coupon.id == coupon_pk, Coupon.profile_id == profile_id)
    ).scalar_one_or_none()


def delete_coupon(db: Session, coupon: Coupon) -> None:
    db.delete(coupon)
    db.commit()


def list_coupons(
    db: Session,
    profile_id: str,
    *,
    search: str | None = None,
    network: str | None = None,
    fiscal_year: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Coupon], int]:
    stmt = select(Coupon).where(Coupon.profile_id == profile_id)
    if search:
        like = f"%{normalize_coupon_code(search)}%"
        stmt = stmt.where(Coupon.normalized_coupon_code.like(like))
    if network:
        stmt = stmt.where(Coupon.network == network)
    if fiscal_year:
        stmt = stmt.where(Coupon.fiscal_year == fiscal_year)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    stmt = stmt.order_by(Coupon.created_at.desc()).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())
    return items, total


def list_all_coupons_for_matching(db: Session, profile_id: str) -> list[Coupon]:
    return list(db.execute(select(Coupon).where(Coupon.profile_id == profile_id)).scalars().all())
