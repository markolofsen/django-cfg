"""Shared OTP types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OTPRequestResult:
    """Result of an OTP send attempt."""

    success: bool
    # 'ok' | 'invalid_email' | 'cooldown' | 'hourly_limit' | 'daily_limit'
    # | 'user_creation_failed' | 'email_send_failed'
    error_code: str = ""
    retry_after: int = 0  # seconds until retry is allowed (0 = no restriction)
