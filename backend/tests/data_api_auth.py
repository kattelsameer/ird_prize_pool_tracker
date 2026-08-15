"""Scenario tables for test_api_auth.py. No imports of code under test."""

VALID_EMAIL = "new-user@example.com"
VALID_PASSWORD = "correct-horse-battery-staple"

# (name, payload, expected_status)
REGISTER_CASES = [
    ("valid", {"email": VALID_EMAIL, "password": VALID_PASSWORD}, 201),
    ("invalid_email", {"email": "not-an-email", "password": VALID_PASSWORD}, 422),
    ("password_too_short", {"email": "short@example.com", "password": "short1"}, 422),
    ("missing_password", {"email": "nopass@example.com"}, 422),
]

# (name, login_payload_relative_to_registered_user, expected_status)
LOGIN_CASES = [
    ("correct_password", {"password": VALID_PASSWORD}, 200),
    ("wrong_password", {"password": "totally-wrong-password"}, 401),
]

UNKNOWN_EMAIL_LOGIN = {"email": "nobody-registered-this@example.com", "password": VALID_PASSWORD}
