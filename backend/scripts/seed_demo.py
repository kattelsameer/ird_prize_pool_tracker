"""Deterministic demo/test fixtures (CLAUDE.md §58).

Loads a fixed set of PrizePoolWinner rows (tagged `source="demo"`, never
`"ird_live"`, so the UI can clearly label this as non-government demo data)
and a handful of sample Coupon rows that exercise every scenario called out
in the spec: a normal non-winning coupon, an active-claim win, an
expiring-claim win (<2 days), an expired-claim win, coupons spanning two
fiscal years, coupons on different networks, and winners across two distinct
draws/periods.

Idempotent: running this multiple times against the same database does not
create duplicate rows (checked via the same (draw_id, prize_coupon_number)
key used by the real sync, and via coupon_code for the sample coupons).

NEVER label this as real government data -- every row's `source` column is
"demo", distinguishable in the API/UI from live-synced `"ird_live"` rows.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.timeutil import now_kathmandu
from app.models.coupon import Coupon
from app.models.prize_pool import PrizePoolWinner
from app.domain.normalization import normalize_coupon_code
from app.repositories.coupon_repo import create_coupon
from app.repositories.network_repo import ensure_default_networks
from app.repositories.profile_repo import get_or_create_default_profile
from sqlalchemy import select

logger = logging.getLogger("scripts.seed_demo")

DEMO_SOURCE = "demo"


def _demo_winner_rows(now):
    published_recent = now - timedelta(days=3)
    published_long_ago = now - timedelta(days=30)

    def raw(draw_id, title, extra=None):
        payload = {
            "draw_id": draw_id,
            "title_en": title,
            "note": "DEMO FIXTURE DATA -- not real IRD data",
        }
        if extra:
            payload.update(extra)
        return payload

    return [
        # Active claim (published 3 days ago, deadline in 12 more days)
        dict(
            draw_id="demo-draw-active",
            category_title_en="Daily Prize",
            category_title_ne="दैनिक पुरस्कार",
            draw_type="GENERAL",
            draw_title_en="Demo Daily Winner Selection (Active Claim)",
            draw_title_ne="नमूना दैनिक विजेता छनौट",
            eligible_from=date(2026, 7, 17),
            eligible_to=date(2026, 7, 31),
            published_at=published_recent,
            claim_deadline=published_recent + timedelta(days=15),
            claim_open=True,
            winner_rank=3,
            prize_fiscal_year_code="2083-84",
            prize_coupon_number="900000000001",
        ),
        # Expiring claim (<2 days remaining from now)
        dict(
            draw_id="demo-draw-expiring",
            category_title_en="Daily Prize",
            category_title_ne="दैनिक पुरस्कार",
            draw_type="GENERAL",
            draw_title_en="Demo Daily Winner Selection (Expiring Claim)",
            draw_title_ne="नमूना दैनिक विजेता छनौट",
            eligible_from=date(2026, 7, 1),
            eligible_to=date(2026, 7, 16),
            published_at=now - timedelta(days=14),
            claim_deadline=now + timedelta(hours=20),
            claim_open=True,
            winner_rank=1,
            prize_fiscal_year_code="2083-84",
            prize_coupon_number="900000000002",
        ),
        # Expired claim (deadline already passed)
        dict(
            draw_id="demo-draw-expired",
            category_title_en="Bumper Prize",
            category_title_ne="बम्पर पुरस्कार",
            draw_type="GENERAL",
            draw_title_en="Demo Bumper Winner Selection (Expired Claim)",
            draw_title_ne="नमूना बम्पर विजेता छनौट",
            eligible_from=date(2026, 6, 1),
            eligible_to=date(2026, 6, 15),
            published_at=published_long_ago,
            claim_deadline=published_long_ago + timedelta(days=15),
            claim_open=True,
            winner_rank=1,
            prize_fiscal_year_code="2082-83",
            prize_coupon_number="900000000003",
        ),
        # Second fiscal year / different period, same-ish shape, non-winning
        # target for the "non_winning_coupon" fixture below (no coupon matches it).
        dict(
            draw_id="demo-draw-other-fy",
            category_title_en="Daily Prize",
            category_title_ne="दैनिक पुरस्कार",
            draw_type="GENERAL",
            draw_title_en="Demo Daily Winner Selection (Other Fiscal Year)",
            draw_title_ne="नमूना दैनिक विजेता छनौट",
            eligible_from=date(2025, 7, 16),
            eligible_to=date(2025, 7, 31),
            published_at=published_long_ago,
            claim_deadline=published_long_ago + timedelta(days=15),
            claim_open=True,
            winner_rank=5,
            prize_fiscal_year_code="2082-83",
            prize_coupon_number="900000000004",
        ),
    ]


def _demo_coupons():
    # (coupon_code, transaction_date, fiscal_year, network)
    return [
        ("900000000001", date(2026, 7, 20), "2083-84", "eSewa"),  # active claim win
        ("900000000002", date(2026, 7, 10), "2083-84", "Khalti"),  # expiring claim win
        ("900000000003", date(2026, 6, 5), "2082-83", "Cash/Manual"),  # expired claim win
        ("111122223333", date(2026, 7, 22), "2083-84", "IME Pay"),  # normal non-winning coupon
        ("444455556666", date(2025, 7, 20), "2082-83", "Bank Transfer"),  # non-winning, other FY
    ]


def seed_demo_data(db: Session) -> None:
    now = now_kathmandu()
    profile = get_or_create_default_profile(db)
    ensure_default_networks(db)

    inserted_winners = 0
    for kwargs in _demo_winner_rows(now):
        existing = db.execute(
            select(PrizePoolWinner).where(
                PrizePoolWinner.draw_id == kwargs["draw_id"],
                PrizePoolWinner.prize_coupon_number == kwargs["prize_coupon_number"],
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue
        row = PrizePoolWinner(
            source_record_id=f"{kwargs['draw_id']}:{kwargs['prize_coupon_number']}",
            normalized_coupon_code=normalize_coupon_code(kwargs["prize_coupon_number"]),
            raw_draw_json={
                "draw_id": kwargs["draw_id"],
                "title_en": kwargs["draw_title_en"],
                "note": "DEMO FIXTURE DATA -- not real IRD data",
            },
            source=DEMO_SOURCE,
            **kwargs,
        )
        db.add(row)
        inserted_winners += 1
    db.commit()

    inserted_coupons = 0
    for coupon_code, txn_date, fiscal_year, network in _demo_coupons():
        normalized = normalize_coupon_code(coupon_code)
        existing = db.execute(
            select(Coupon).where(
                Coupon.profile_id == profile.id, Coupon.normalized_coupon_code == normalized
            )
        ).scalar_one_or_none()
        if existing is not None:
            continue
        create_coupon(
            db,
            profile_id=profile.id,
            coupon_code=coupon_code,
            transaction_date=txn_date,
            fiscal_year=fiscal_year,
            network=network,
        )
        inserted_coupons += 1

    logger.info(
        "Demo seed complete: %s new winner rows, %s new coupon rows",
        inserted_winners,
        inserted_coupons,
    )


if __name__ == "__main__":
    from app.core.db import SessionLocal
    from app.models import Base
    from app.core.db import engine

    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        seed_demo_data(session)
    finally:
        session.close()
