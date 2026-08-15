"""Scenario tables for test_api_settings.py. No imports of code under test."""

# (name, put_payload, expected_field, expected_value)
UPDATE_SETTINGS_CASES = [
    ("disable_new_match", {"notify_new_match": False}, "notify_new_match", False),
    ("disable_claim_expiring", {"notify_claim_expiring": False}, "notify_claim_expiring", False),
    ("enable_sync_failures", {"notify_sync_failures": True}, "notify_sync_failures", True),
]

NEW_NETWORK_NAME = "ConnectIPS"
