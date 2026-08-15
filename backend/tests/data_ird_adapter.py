"""Scenario tables for test_ird_adapter.py. No imports of code under test."""

VALID_PAGE_PAYLOAD = {
    "limit": 6,
    "offset": 0,
    "total_draws": 2,
    "has_more": False,
    "fiscal_years": [
        {"fiscal_year_code": "2083-84", "display_name": "FY 2083/84", "winner_count": 16},
        {"fiscal_year_code": "2082-83", "display_name": "FY 2082/83", "winner_count": 0},
    ],
    "categories": [
        {"category_id": "category_11e8", "title_en": "Bumper Prize", "title_ne": "बम्पर पुरस्कार"},
        {"category_id": "category_31dc", "title_en": "Daily Prize", "title_ne": "दैनिक पुरस्कार"},
    ],
    "draws": [
        {
            "draw_id": "draw_3dcfe8001afc31a805736567ea3ea74f",
            "category_title_en": "Bumper Prize",
            "category_title_ne": "बम्पर पुरस्कार",
            "draw_type": "GENERAL",
            "title_en": "Bumper Winner Consumer Selection for the period of Shrawan 1 to 15",
            "title_ne": "श्रावण १ गते देखी १५ गतेसम्मको बम्पर विजेता उपभोक्ता छनौट",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46.293223+05:45",
            "claim_deadline": "2026-08-22T09:27:46.293223+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "007315254493"}
            ],
        }
    ],
}

# A draw whose winner entry is missing prize_coupon_number -- must be skipped,
# not fatal to the whole page (CLAUDE.md §10e "partial data").
PARTIAL_DATA_PAYLOAD = {
    "limit": 6,
    "offset": 0,
    "total_draws": 1,
    "has_more": False,
    "draws": [
        {
            "draw_id": "draw_partial",
            "category_title_en": "Daily Prize",
            "draw_type": "GENERAL",
            "title_en": "Daily Winner Selection",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46+05:45",
            "claim_deadline": "2026-08-22T09:27:46+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "007315254493"},
                {"winner_rank": 2, "prize_fiscal_year_code": "2083-84"},  # missing coupon number
            ],
        }
    ],
}

# Draw missing optional fields entirely (category_title_ne, title_ne) -- must
# not raise (CLAUDE.md §10e "missing government fields").
MISSING_OPTIONAL_FIELDS_PAYLOAD = {
    "limit": 6,
    "offset": 0,
    "total_draws": 1,
    "has_more": False,
    "draws": [
        {
            "draw_id": "draw_sparse",
            "draw_type": "GENERAL",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46+05:45",
            "claim_deadline": "2026-08-22T09:27:46+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "007315254493"},
            ],
        }
    ],
}

EMPTY_PAGE_PAYLOAD = {
    "limit": 6,
    "offset": 0,
    "total_draws": 0,
    "has_more": False,
    "draws": [],
}

# Duplicate winner entries within a single page (same draw_id + coupon number
# twice) -- the adapter itself does not dedupe (that's the persistence layer's
# job via the unique key); this documents/exercises that the adapter faithfully
# passes through both so the persistence-layer contract can be relied upon.
DUPLICATE_WINNER_IN_PAGE_PAYLOAD = {
    "limit": 6,
    "offset": 0,
    "total_draws": 1,
    "has_more": False,
    "draws": [
        {
            "draw_id": "draw_dup",
            "draw_type": "GENERAL",
            "eligible_from": "2026-07-17",
            "eligible_to": "2026-07-31",
            "published_at": "2026-08-07T09:27:46+05:45",
            "claim_deadline": "2026-08-22T09:27:46+05:45",
            "claim_open": True,
            "winners": [
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "007315254493"},
                {"winner_rank": 1, "prize_fiscal_year_code": "2083-84", "prize_coupon_number": "007315254493"},
            ],
        }
    ],
}

MALFORMED_PAYLOADS = [
    ("not_a_dict", ["this", "is", "a", "list"]),
    ("missing_draws_key", {"limit": 6, "offset": 0, "has_more": False}),
    ("draws_not_a_list", {"limit": 6, "offset": 0, "has_more": False, "draws": "oops"}),
    (
        "missing_published_at",
        {
            "limit": 6,
            "offset": 0,
            "has_more": False,
            "draws": [
                {
                    "draw_id": "d1",
                    "claim_deadline": "2026-08-22T09:27:46+05:45",
                    "winners": [],
                }
            ],
        },
    ),
]
