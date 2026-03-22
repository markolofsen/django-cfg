"""
Email validation service for OTP authentication.

Only validates syntax (RFC 5321/5322) and normalizes the address.
No network calls, no blocklists — if the email is syntactically valid,
we accept it. If it's fake, the OTP simply won't arrive.

Usage
-----
    from django_cfg.apps.system.accounts.services.email_validator import validate_email_address

    try:
        normalized = validate_email_address("User@Example.COM")
    except EmailValidationError as exc:
        return error_response(exc.error_code, str(exc))
"""

from __future__ import annotations

from email_validator import validate_email  # type: ignore


class EmailValidationError(Exception):
    """Raised when an email address fails validation."""

    def __init__(self, message: str, error_code: str = "invalid_email") -> None:
        super().__init__(message)
        self.error_code = error_code


def validate_email_address(email: str) -> str:
    """Validate and normalize an email address.

    Returns the normalized (lowercased) email on success.
    Raises EmailValidationError if syntax is invalid.
    """
    email = email.strip()
    if not email:
        raise EmailValidationError("Email address is required.", "invalid_email")

    try:
        info = validate_email(email, check_deliverability=False)
        return info.normalized.lower()
    except Exception as exc:
        raise EmailValidationError(
            f"Invalid email address: {exc}",
            "invalid_email",
        ) from exc
