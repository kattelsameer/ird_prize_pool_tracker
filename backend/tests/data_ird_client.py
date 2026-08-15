"""Scenario tables for test_ird_client.py. No imports of code under test."""

PAGE_0 = {
    "limit": 2,
    "offset": 0,
    "total_draws": 2,
    "has_more": True,
    "draws": [
        {
            "draw_id": "draw_1",
            "draw_type": "GENERAL",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46+05:45",
            "claim_deadline": "2026-08-22T09:27:46+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "111111111111"}
            ],
        }
    ],
}

PAGE_1 = {
    "limit": 2,
    "offset": 2,
    "total_draws": 2,
    "has_more": False,
    "draws": [
        {
            "draw_id": "draw_2",
            "draw_type": "GENERAL",
            "eligible_from": "2026-08-01",
            "eligible_to": "2026-08-15",
            "published_at": "2026-08-22T09:27:46+05:45",
            "claim_deadline": "2026-09-06T09:27:46+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "222222222222"}
            ],
        }
    ],
}

TWO_PAGE_RESPONSES_BY_OFFSET = {0: PAGE_0, 2: PAGE_1}

SINGLE_EMPTY_PAGE = {
    "limit": 100,
    "offset": 0,
    "total_draws": 0,
    "has_more": False,
    "draws": [],
}
