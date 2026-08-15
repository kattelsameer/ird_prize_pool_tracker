"""Scenario tables for test_matching.py. No imports of code under test.

Covers CLAUDE.md §50 matching-engine scenarios as plain data. `test_matching.py`
builds CouponInput/WinnerInput dataclass instances from these tuples and feeds
them through `match_coupons`.
"""
from datetime import date, datetime, timedelta, timezone

KTM = timezone(timedelta(hours=5, minutes=45))
NOW = datetime(2026, 8, 10, 12, 0, 0, tzinfo=KTM)

PUBLISHED_AT = datetime(2026, 8, 7, 9, 27, 46, tzinfo=KTM)
CLAIM_DEADLINE_ACTIVE = PUBLISHED_AT + timedelta(days=15)  # 2026-08-22, still active at NOW
CLAIM_DEADLINE_EXPIRING = NOW + timedelta(hours=20)  # < 2 days away from NOW
CLAIM_DEADLINE_EXPIRED = NOW - timedelta(days=1)  # already passed
CLAIM_DEADLINE_EXACT_BOUNDARY = NOW  # exactly at "now"

DEFAULT_WINNER_KWARGS = dict(
    eligible_from=date(2026, 7, 17),
    eligible_to=date(2026, 7, 31),
    published_at=PUBLISHED_AT,
    winner_rank=1,
    category_title_en="Daily Prize",
    draw_type="GENERAL",
    draw_title_en="Daily Winner Consumer Selection for the period of Shrawan 1 to 15",
)

# --- Coupons -----------------------------------------------------------
# (name, coupon_id, coupon_code, fiscal_year, transaction_date)
COUPONS = {
    "exact_winner": ("c-exact", "007315254493", "2083-84", date(2026, 7, 20)),
    "non_winner": ("c-nonwin", "111111111111", "2083-84", date(2026, 7, 20)),
    "winner_wrong_fy": ("c-wrongfy", "007315254493", "2082-83", date(2026, 7, 20)),
    "winner_no_fy": ("c-nofy", "007315254493", None, date(2026, 7, 20)),
    "winner_date_before_period": ("c-before", "007315254493", "2083-84", date(2026, 7, 1)),
    "winner_date_after_period": ("c-after", "007315254493", "2083-84", date(2026, 8, 15)),
    "winner_date_on_start_boundary": ("c-start-boundary", "007315254493", "2083-84", date(2026, 7, 17)),
    "winner_date_on_end_boundary": ("c-end-boundary", "007315254493", "2083-84", date(2026, 7, 31)),
    "winner_missing_transaction_date": ("c-nodate", "007315254493", "2083-84", None),
    "duplicate_entry_a": ("c-dup-a", "007315254493", "2083-84", date(2026, 7, 20)),
    "duplicate_entry_b": ("c-dup-b", "007315254493", "2083-84", date(2026, 7, 20)),
    "coupon_needs_normalization": ("c-messy", "007 315 254 493", "2083-84", date(2026, 7, 20)),
}

# --- Winners -------------------------------------------------------------
# name -> dict of override kwargs merged onto DEFAULT_WINNER_KWARGS, plus
# draw_id / prize_coupon_number / prize_fiscal_year_code / claim_deadline / claim_open
WINNERS = {
    "primary": dict(
        draw_id="draw-1",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2083-84",
        claim_deadline=CLAIM_DEADLINE_ACTIVE,
        claim_open=True,
    ),
    "other_period_same_code": dict(
        draw_id="draw-2",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2082-83",
        claim_deadline=CLAIM_DEADLINE_ACTIVE,
        claim_open=True,
        eligible_from=date(2025, 7, 16),
        eligible_to=date(2025, 7, 31),
    ),
    "expiring_claim": dict(
        draw_id="draw-3",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2083-84",
        claim_deadline=CLAIM_DEADLINE_EXPIRING,
        claim_open=True,
    ),
    "expired_claim": dict(
        draw_id="draw-4",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2083-84",
        claim_deadline=CLAIM_DEADLINE_EXPIRED,
        claim_open=True,
    ),
    "expired_because_closed": dict(
        draw_id="draw-5",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2083-84",
        claim_deadline=CLAIM_DEADLINE_ACTIVE,
        claim_open=False,
    ),
    "claim_deadline_exact_boundary": dict(
        draw_id="draw-6",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2083-84",
        claim_deadline=CLAIM_DEADLINE_EXACT_BOUNDARY,
        claim_open=True,
    ),
    "missing_optional_fields": dict(
        draw_id="draw-7",
        prize_coupon_number="007315254493",
        prize_fiscal_year_code="2083-84",
        claim_deadline=CLAIM_DEADLINE_ACTIVE,
        claim_open=True,
        eligible_from=None,
        eligible_to=None,
    ),
}

# --- Scenarios: (name, coupon_key, winner_keys, expect_match, expected_checks) --
# expected_checks is a dict of assertions applied to the single MatchResult
# (only used when exactly one match is expected).
SCENARIOS = [
    dict(
        name="exact_winning_coupon_matches",
        coupon_key="exact_winner",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"fiscal_year_unconfirmed": False, "eligible_period_warning": False},
    ),
    dict(
        name="non_winning_coupon_has_no_match",
        coupon_key="non_winner",
        winner_keys=["primary"],
        expect_match_count=0,
        checks={},
    ),
    dict(
        name="same_code_different_fiscal_year_period_both_surface",
        coupon_key="exact_winner",
        winner_keys=["primary", "other_period_same_code"],
        expect_match_count=2,
        checks={},
    ),
    dict(
        name="fiscal_year_mismatch_flagged_not_excluded",
        coupon_key="winner_wrong_fy",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"fiscal_year_unconfirmed": True},
    ),
    dict(
        name="missing_user_fiscal_year_still_matches_unconfirmed_false",
        coupon_key="winner_no_fy",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"fiscal_year_unconfirmed": False},
    ),
    dict(
        name="transaction_date_before_eligible_period_still_matches_with_warning",
        coupon_key="winner_date_before_period",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"eligible_period_warning": True},
    ),
    dict(
        name="transaction_date_after_eligible_period_still_matches_with_warning",
        coupon_key="winner_date_after_period",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"eligible_period_warning": True},
    ),
    dict(
        name="transaction_date_on_start_boundary_no_warning",
        coupon_key="winner_date_on_start_boundary",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"eligible_period_warning": False},
    ),
    dict(
        name="transaction_date_on_end_boundary_no_warning",
        coupon_key="winner_date_on_end_boundary",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"eligible_period_warning": False},
    ),
    dict(
        name="missing_transaction_date_no_warning",
        coupon_key="winner_missing_transaction_date",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"eligible_period_warning": False},
    ),
    dict(
        name="missing_optional_government_fields_still_matches",
        coupon_key="winner_date_before_period",
        winner_keys=["missing_optional_fields"],
        expect_match_count=1,
        checks={"eligible_period_warning": False},
    ),
    dict(
        name="active_claim",
        coupon_key="exact_winner",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={"claim_status": "CLAIM_ACTIVE"},
    ),
    dict(
        name="expiring_claim_under_2_days",
        coupon_key="exact_winner",
        winner_keys=["expiring_claim"],
        expect_match_count=1,
        checks={"claim_status": "CLAIM_EXPIRING"},
    ),
    dict(
        name="expired_claim_past_deadline",
        coupon_key="exact_winner",
        winner_keys=["expired_claim"],
        expect_match_count=1,
        checks={"claim_status": "CLAIM_EXPIRED"},
    ),
    dict(
        name="expired_claim_because_claim_closed",
        coupon_key="exact_winner",
        winner_keys=["expired_because_closed"],
        expect_match_count=1,
        checks={"claim_status": "CLAIM_EXPIRED"},
    ),
    dict(
        name="claim_deadline_exact_boundary_is_expired",
        coupon_key="exact_winner",
        winner_keys=["claim_deadline_exact_boundary"],
        expect_match_count=1,
        checks={"claim_status": "CLAIM_EXPIRED"},
    ),
    dict(
        name="coupon_code_requiring_normalization_still_matches",
        coupon_key="coupon_needs_normalization",
        winner_keys=["primary"],
        expect_match_count=1,
        checks={},
    ),
]

# Duplicate user coupon entries: two separate Coupon rows with the same code
# should each independently produce their own match (the app layer, not the
# matching engine, is responsible for warning the user about the duplicate
# entry per CLAUDE.md's "duplicate-coupon-entry guard" product improvement).
DUPLICATE_USER_COUPON_SCENARIO = dict(
    coupon_keys=["duplicate_entry_a", "duplicate_entry_b"],
    winner_keys=["primary"],
    expected_total_matches=2,
)

# Duplicate government records: the SAME (draw_id, prize_coupon_number) pair
# appearing twice (e.g. a sync bug producing two WinnerInput objects for one
# real winner) must not cause the matching engine itself to crash; the
# de-duplication contract lives at persistence (unique key), but the matching
# engine's behavior with an accidental duplicate WinnerInput list is exercised
# here for defense-in-depth: it will surface both (upstream persistence is
# responsible for preventing this from happening in practice).
DUPLICATE_GOVERNMENT_RECORD_SCENARIO = dict(
    coupon_key="exact_winner",
    duplicated_winner_key="primary",
    expected_total_matches=2,
)
