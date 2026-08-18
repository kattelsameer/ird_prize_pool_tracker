"""Scenario tables for test_nepali_calendar.py. No imports of code under test."""
from datetime import date

# (name, gregorian_date, expected_fiscal_year_code)
# Anchor values taken verbatim from CLAUDE.md's own worked example:
#   "A transaction on July 16, 2026 (Gregorian) falls in the previous fiscal
#    year (2082-83 in BS). A transaction on July 17, 2026 falls in fiscal year
#    2083-84."
FISCAL_YEAR_BOUNDARY_CASES = [
    ("day_before_boundary_is_prior_fy", date(2026, 7, 16), "2082-83"),
    ("boundary_day_is_new_fy", date(2026, 7, 17), "2083-84"),
    ("well_into_new_fy", date(2026, 8, 1), "2083-84"),
    ("well_into_prior_fy", date(2025, 12, 1), "2082-83"),
]

# (name, gregorian_date, expected_period_start, expected_period_end, expected_publish_date)
# Verified against the real `nepali_datetime` conversion:
#   Shrawan 1-15 2083  = 2026-07-17 .. 2026-07-31, published Shrawan 16  = 2026-08-01
#   Shrawan 16-31 2083 = 2026-08-01 .. 2026-08-16, published Bhadra 1   = 2026-08-17
#   Bhadra 1-15 2083   = 2026-08-17 .. 2026-08-31, published Bhadra 16  = 2026-09-01
HALF_MONTH_PERIOD_CASES = [
    (
        "first_half_of_shrawan",
        date(2026, 7, 20),
        date(2026, 7, 17),
        date(2026, 7, 31),
        date(2026, 8, 1),
    ),
    (
        "second_half_start_boundary",
        date(2026, 8, 1),
        date(2026, 8, 1),
        date(2026, 8, 16),
        date(2026, 8, 17),
    ),
    (
        "second_half_end_boundary",
        date(2026, 8, 16),
        date(2026, 8, 1),
        date(2026, 8, 16),
        date(2026, 8, 17),
    ),
    (
        "next_month_first_half_start",
        date(2026, 8, 17),
        date(2026, 8, 17),
        date(2026, 8, 31),
        date(2026, 9, 1),
    ),
    (
        "next_month_first_half_middle",
        date(2026, 8, 18),
        date(2026, 8, 17),
        date(2026, 8, 31),
        date(2026, 9, 1),
    ),
]
