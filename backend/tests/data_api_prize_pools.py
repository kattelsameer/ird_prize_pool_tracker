"""Scenario tables/builders for test_api_prize_pools.py. No imports of code under test.

Claim-status boundaries are computed relative to "now" at call time (rather than a
fixed literal datetime) because the /api/prize-pools endpoint derives claim_status
from app.core.timeutil.now_kathmandu() internally -- a hardcoded past/future date
would eventually drift into the wrong bucket.
"""
from __future__ import annotations

from datetime import timedelta

# ── Fixtures / builders ──────────────────────────────────────────────

# (row_kwargs_overrides keyed by name) -- draw_id/prize_coupon_number/category_title_en/
# published_at/eligible_from/eligible_to are fixed; claim_deadline is relative to `now`.
def build_winner_rows(now):
    return [
        dict(
            name="active_bumper",
            source_record_id="src-active-bumper",
            draw_id="draw-active",
            category_title_en="Bumper Prize",
            draw_type="GENERAL",
            draw_title_en="Active Bumper Draw",
            eligible_from=None,
            eligible_to=None,
            published_at=now - timedelta(days=1),
            claim_deadline=now + timedelta(days=10),
            claim_open=True,
            winner_rank=1,
            prize_fiscal_year_code="2083-84",
            prize_coupon_number="100000000001",
            normalized_coupon_code="100000000001",
        ),
        dict(
            name="expiring_daily",
            source_record_id="src-expiring-daily",
            draw_id="draw-expiring",
            category_title_en="Daily Prize",
            draw_type="GENERAL",
            draw_title_en="Expiring Daily Draw",
            eligible_from=None,
            eligible_to=None,
            published_at=now - timedelta(days=5),
            claim_deadline=now + timedelta(hours=20),
            claim_open=True,
            winner_rank=1,
            prize_fiscal_year_code="2083-84",
            prize_coupon_number="200000000002",
            normalized_coupon_code="200000000002",
        ),
        dict(
            name="expired_daily",
            source_record_id="src-expired-daily",
            draw_id="draw-expired",
            category_title_en="Daily Prize",
            draw_type="GENERAL",
            draw_title_en="Expired Daily Draw",
            eligible_from=None,
            eligible_to=None,
            published_at=now - timedelta(days=20),
            claim_deadline=now - timedelta(days=1),
            claim_open=True,
            winner_rank=2,
            prize_fiscal_year_code="2082-83",
            prize_coupon_number="300000000003",
            normalized_coupon_code="300000000003",
        ),
    ]


# ── list_prize_pools_endpoint sort scenarios ─────────────────────────
# (name, sort_query_value, expected_first_prize_coupon_number)
SORT_CASES = [
    ("published_at_desc_default", None, "100000000001"),  # most recently published first
    ("published_at_asc", "published_at", "300000000003"),
    ("coupon_code_asc", "coupon_code", "100000000001"),
    ("coupon_code_desc", "-coupon_code", "300000000003"),
]

# ── list_prize_pools_endpoint claim_status scenarios ─────────────────
# (name, claim_status_query_value, expected_prize_coupon_numbers)
CLAIM_STATUS_CASES = [
    ("active_only", "CLAIM_ACTIVE", {"100000000001"}),
    ("expiring_only", "CLAIM_EXPIRING", {"200000000002"}),
    ("expired_only", "CLAIM_EXPIRED", {"300000000003"}),
]
