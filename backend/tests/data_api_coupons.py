"""Scenario tables for test_api_coupons.py. No imports of code under test."""

# (name, payload, expected_status)
CREATE_COUPON_CASES = [
    (
        "full_payload",
        {
            "coupon_code": "007315254493",
            "transaction_date": "2026-07-20",
            "fiscal_year": "2083-84",
            "network": "eSewa",
        },
        201,
    ),
    (
        "coupon_code_only",
        {"coupon_code": "111122223333"},
        201,
    ),
    (
        "blank_coupon_code_rejected",
        {"coupon_code": "   "},
        422,
    ),
    (
        "missing_coupon_code_rejected",
        {"transaction_date": "2026-07-20"},
        422,
    ),
]

DUPLICATE_COUPON_PAYLOAD = {
    "coupon_code": "222233334444",
    "transaction_date": "2026-07-20",
    "fiscal_year": "2083-84",
    "network": "Khalti",
}
