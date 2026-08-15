"""Scenario tables for test_normalization.py. No imports of code under test."""

# (name, raw_code, expected_normalized)
COUPON_CODE_CASES = [
    ("clean_12_digit", "007315254493", "007315254493"),
    ("with_spaces", "007 315 254 493", "007315254493"),
    ("with_hyphens", "007-315-254-493", "007315254493"),
    ("lowercase_suffix", "007315254493bumper", "007315254493BUMPER"),
    ("mixed_spaces_and_suffix", "007 315 254 493BUMPER", "007315254493BUMPER"),
    ("leading_trailing_whitespace", "  007315254493  ", "007315254493"),
    ("empty_string", "", ""),
]

# (name, raw_fy, expected_normalized)
FISCAL_YEAR_CASES = [
    ("canonical", "2083-84", "2083-84"),
    ("slash_separator", "2083/84", "2083-84"),
    ("whitespace", " 2083 - 84 ", "2083-84"),
    ("four_digit_end", "2083-2084", "2083-84"),
    ("none_value", None, None),
    ("blank_value", "   ", None),
]

# (name, raw_network, expected_normalized)
NETWORK_CASES = [
    ("esewa", "eSewa", "eSewa"),
    ("extra_internal_whitespace", "IME   Pay", "IME Pay"),
    ("leading_trailing", "  Khalti  ", "Khalti"),
    ("none_value", None, None),
    ("blank_value", "   ", None),
]
