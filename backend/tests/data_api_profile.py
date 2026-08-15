"""Scenario tables for test_api_profile.py. No imports of code under test."""

# (name, put_payload, expected_display_name)
UPDATE_PROFILE_CASES = [
    ("set_display_name", {"display_name": "Ram Bahadur"}, "Ram Bahadur"),
    ("clear_display_name", {"display_name": None}, None),
]
