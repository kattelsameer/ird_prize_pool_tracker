"""Scenario tables for test_claim_status.py. No imports of code under test."""
from datetime import datetime, timedelta, timezone

KTM = timezone(timedelta(hours=5, minutes=45))

_DEADLINE = datetime(2026, 8, 22, 9, 27, 46, tzinfo=KTM)

# (name, now, claim_deadline, claim_open, expected_status_value)
CLAIM_STATUS_CASES = [
    (
        "active_well_before_deadline",
        _DEADLINE - timedelta(days=10),
        _DEADLINE,
        True,
        "CLAIM_ACTIVE",
    ),
    (
        "expiring_just_under_2_days",
        _DEADLINE - timedelta(hours=47),
        _DEADLINE,
        True,
        "CLAIM_EXPIRING",
    ),
    (
        "expiring_exactly_at_2_day_threshold_minus_1_second",
        _DEADLINE - timedelta(days=2) + timedelta(seconds=1),
        _DEADLINE,
        True,
        "CLAIM_EXPIRING",
    ),
    (
        "active_exactly_at_2_day_threshold",
        _DEADLINE - timedelta(days=2),
        _DEADLINE,
        True,
        "CLAIM_ACTIVE",
    ),
    (
        "expired_exactly_at_deadline_boundary",
        _DEADLINE,
        _DEADLINE,
        True,
        "CLAIM_EXPIRED",
    ),
    (
        "expired_past_deadline",
        _DEADLINE + timedelta(days=1),
        _DEADLINE,
        True,
        "CLAIM_EXPIRED",
    ),
    (
        "expired_because_claim_closed_even_though_before_deadline",
        _DEADLINE - timedelta(days=5),
        _DEADLINE,
        False,
        "CLAIM_EXPIRED",
    ),
]

# (name, now, claim_deadline) -- both naive, should raise ValueError
NAIVE_DATETIME_CASES = [
    ("naive_now", datetime(2026, 8, 10), _DEADLINE),
    ("naive_deadline", _DEADLINE, datetime(2026, 8, 22)),
]
