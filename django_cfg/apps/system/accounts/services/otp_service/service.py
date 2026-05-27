"""``OTPService`` — thin façade preserving the historical public API.

Internally, request and verify each live in their own module so they
can be unit-tested in isolation; this class is just the import surface
external code (auth views, management commands, tests) already uses:

    from django_cfg.apps.system.accounts.services import OTPService

    OTPService.request_otp(email, source_url=..., accept_language=...)
    OTPService.verify_otp(email, otp_code, source_url=..., ip_address=...)
"""

from __future__ import annotations

from typing import Optional

from django_cfg.core.utils import get_otp_url

from ...models import CustomUser
from .request import request_otp as _request_otp
from .types import OTPRequestResult
from .verify import verify_otp as _verify_otp


class OTPService:
    """Simple OTP service for authentication."""

    # Backward-compat: callers historically reached for this attribute
    _get_otp_url = staticmethod(get_otp_url)

    @staticmethod
    def request_otp(
        email: str,
        source_url: Optional[str] = None,
        accept_language: Optional[str] = None,
    ) -> OTPRequestResult:
        """Generate and send OTP to email. Returns OTPRequestResult."""
        return _request_otp(email, source_url=source_url, accept_language=accept_language)

    @staticmethod
    def verify_otp(
        email: str,
        otp_code: str,
        source_url: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[CustomUser]:
        """Verify OTP and return user if valid; ``None`` on any failure."""
        return _verify_otp(email, otp_code, source_url=source_url, ip_address=ip_address)
