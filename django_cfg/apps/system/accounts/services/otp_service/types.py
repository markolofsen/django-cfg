"""Shared OTP types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConsentCapture:
    """Marketing-consent intent captured alongside an OTP request.

    ``marketing_consent`` is ``None`` when the client sent no choice —
    distinguishable from an explicit ``False`` (declined).
    """

    marketing_consent: Optional[bool] = None
    disclosure_version: str = ""
    jurisdiction_hint: str = ""  # normalized CF-IPCountry, or ""


@dataclass
class OTPRequestResult:
    """Result of an OTP send attempt."""

    success: bool
    # 'ok' | 'invalid_email' | 'cooldown' | 'hourly_limit' | 'daily_limit'
    # | 'user_creation_failed'
    error_code: str = ""
    retry_after: int = 0  # seconds until retry is allowed (0 = no restriction)
    resend_in: int = 0  # success: seconds until a new code may be requested
    expires_in: int = 0  # success: seconds the code stays valid
