"""Scenario tables for test_sync_service.py. No imports of code under test.

Payload shapes mirror the real IRD API response (see RESEARCH.md / CLAUDE.md
§8) so tests exercise the full IrdClient -> adapter -> sync_service path with
only the HTTP transport mocked (via httpx.MockTransport in the test file).
"""

# (name, consecutive_failures_including_this_one, expected_retry_delay_seconds)
# CLAUDE.md §10e: retry after 1h, then 4h, then 24h (clamped after that).
RETRY_BACKOFF_CASES = [
    ("first_failure", 1, 3600),
    ("second_failure", 2, 14400),
    ("third_failure", 3, 86400),
    ("fourth_failure_stays_at_24h", 4, 86400),
    ("tenth_failure_stays_at_24h", 10, 86400),
]

INITIAL_SYNC_PAGE = {
    "limit": 100,
    "offset": 0,
    "total_draws": 1,
    "has_more": False,
    "draws": [
        {
            "draw_id": "sync-test-draw-1",
            "category_title_en": "Daily Prize",
            "draw_type": "GENERAL",
            "title_en": "Sync Test Draw",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46+05:45",
            "claim_deadline": "2026-08-22T09:27:46+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "300000000001"},
                {"winner_rank": 2, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "300000000002"},
            ],
        }
    ],
}

# Same draw_id + same coupons, but claim_open flipped to False -- simulates a
# government record update on re-sync (CLAUDE.md §10e "government record
# update on re-sync (claim_open flips)").
UPDATED_SYNC_PAGE = {
    "limit": 100,
    "offset": 0,
    "total_draws": 1,
    "has_more": False,
    "draws": [
        {
            "draw_id": "sync-test-draw-1",
            "category_title_en": "Daily Prize",
            "draw_type": "GENERAL",
            "title_en": "Sync Test Draw",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46+05:45",
            "claim_deadline": "2026-08-22T09:27:46+05:45",
            "claim_open": False,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "300000000001"},
                {"winner_rank": 2, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "300000000002"},
            ],
        }
    ],
}
