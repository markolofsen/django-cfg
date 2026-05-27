"""OTP service package — preserves the historical public API.

External imports keep working unchanged:

    from django_cfg.apps.system.accounts.services.otp_service import OTPService
    from django_cfg.apps.system.accounts.services import OTPService  # re-exported via services/__init__.py
"""

from .service import OTPService
from .types import OTPRequestResult

__all__ = ["OTPService", "OTPRequestResult"]
