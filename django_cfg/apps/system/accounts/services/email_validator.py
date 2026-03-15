"""
Email validation service for OTP authentication.

Layers (applied in order, cheapest first):

  1. Syntax — RFC 5321/5322 via email-validator (rejects invalid local parts,
     malformed domains, special-use TLDs, unsafe Unicode, etc.)
  2. Numeric TLD — catches typo domains like gmail.com1, yahoo.net2
  3. Suspicious local part — rejects repeated special chars: m*****@, a..b@, etc.
  4. Disposable domains — blocklist of ~5 000 throwaway email services
  5. MX / deliverability — DNS lookup to confirm the domain accepts mail
     (optional, ~100 ms, skip in unit tests via check_deliverability=False)

Usage
-----
    from django_cfg.apps.system.accounts.services.email_validator import validate_email_address

    try:
        normalized = validate_email_address("User@Example.COM")
    except EmailValidationError as exc:
        return error_response(exc.error_code, str(exc))
"""

from __future__ import annotations

import re

from django_cfg.utils import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class EmailValidationError(Exception):
    """Raised when an email address fails any validation check."""

    def __init__(self, message: str, error_code: str = "invalid_email") -> None:
        super().__init__(message)
        self.error_code = error_code


# ---------------------------------------------------------------------------
# Compiled patterns (module-level, compiled once)
# ---------------------------------------------------------------------------

# Domains ending with one or more digits:  gmail.com1  yahoo.net99
_NUMERIC_TLD_RE = re.compile(r"\.\d+$")

# Two or more consecutive identical special characters in the local part.
# Catches: m*****@  a..b@  test---@  user+++@
_REPEATED_SPECIALS_RE = re.compile(r"([!#$%&'*+/=?^`{|}~\-.])\1+")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_email_address(
    email: str,
    *,
    check_deliverability: bool = True,
) -> str:
    """
    Validate and normalize an email address.

    Returns the normalized (lowercased, NFC-normalized) email on success.
    Raises :class:`EmailValidationError` on any failure.

    Parameters
    ----------
    email:
        Raw input from the user.
    check_deliverability:
        When True (default) performs a DNS/MX lookup to confirm the domain
        can receive mail.  Set to False in unit tests or where latency matters
        and you rely on the syntax + blocklist checks alone.
    """
    email = email.strip()
    if not email:
        raise EmailValidationError("Email address is required.", "invalid_email")

    # ------------------------------------------------------------------
    # Layer 1 — RFC syntax check (email-validator)
    # ------------------------------------------------------------------
    try:
        from email_validator import validate_email  # type: ignore
    except ImportError:
        logger.warning("email-validator not installed; falling back to basic syntax check")
        return _basic_syntax_check(email)

    try:
        info = validate_email(email, check_deliverability=False)
        # RFC technically allows case-sensitive local parts, but in practice
        # all major providers treat them as case-insensitive.  We normalize
        # the full address to lowercase so storage/lookup is consistent.
        normalized: str = info.normalized.lower()
    except Exception as exc:  # EmailNotValidError
        raise EmailValidationError(
            f"Invalid email address: {exc}",
            "invalid_email",
        ) from exc

    local_part, domain = normalized.split("@", 1)
    domain_lower = domain.lower()

    # ------------------------------------------------------------------
    # Layer 2 — Numeric TLD (gmail.com1, yahoo.net2, …)
    # ------------------------------------------------------------------
    if _NUMERIC_TLD_RE.search(domain_lower):
        raise EmailValidationError(
            "The email domain appears to be invalid (numeric TLD).",
            "invalid_email",
        )

    # ------------------------------------------------------------------
    # Layer 3 — Suspicious local part (m*****@, a..b@, user+++@)
    # ------------------------------------------------------------------
    if _REPEATED_SPECIALS_RE.search(local_part):
        raise EmailValidationError(
            "The email address contains invalid repeated characters.",
            "invalid_email",
        )

    # ------------------------------------------------------------------
    # Layer 4 — Disposable domain blocklist (~5 000 domains)
    # ------------------------------------------------------------------
    try:
        from disposable_email_domains import blocklist  # type: ignore

        if domain_lower in blocklist:
            raise EmailValidationError(
                "Disposable email addresses are not accepted.",
                "disposable_email",
            )
    except ImportError:
        logger.warning("disposable-email-domains not installed; skipping disposable check")

    # ------------------------------------------------------------------
    # Layer 5 — MX / deliverability DNS check (optional, ~100 ms)
    # ------------------------------------------------------------------
    if check_deliverability:
        try:
            info2 = validate_email(normalized, check_deliverability=True)
            normalized = info2.normalized.lower()
        except Exception as exc:
            raise EmailValidationError(
                "The email domain does not appear to accept mail.",
                "invalid_email",
            ) from exc

    return normalized


# ---------------------------------------------------------------------------
# Fallback when email-validator is not installed
# ---------------------------------------------------------------------------

_BASIC_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-!#$&'*/=?^`{|}~]+@[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$"
)


def _basic_syntax_check(email: str) -> str:
    """Minimal fallback when email-validator is unavailable."""
    cleaned = email.strip().lower()
    if not _BASIC_EMAIL_RE.match(cleaned):
        raise EmailValidationError("Invalid email address.", "invalid_email")
    return cleaned
