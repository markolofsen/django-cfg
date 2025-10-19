"""
Django Twilio Module for django_cfg.

Auto-configuring Twilio services for OTP and messaging via WhatsApp, Email, and SMS.
Supports both sync and async operations following Django 5.2+ patterns.

Features:
- WhatsApp OTP with SMS fallback
- Email OTP via SendGrid with templates
- SMS OTP via Twilio Verify API
- Unified OTP service with smart channel selection
- Full async/await support
- Type-safe configuration with Pydantic v2
"""

# Configuration
# Services
from django_cfg.modules.django_twilio.base import BaseTwilioService, is_async_context
from django_cfg.modules.django_twilio.email_otp import EmailOTPService

# Exceptions
from django_cfg.modules.django_twilio.exceptions import (
    TwilioConfigurationError,
    TwilioError,
    TwilioSendError,
    TwilioVerificationError,
)
from django_cfg.modules.django_twilio.models import TwilioConfig

# Simple messaging service
from django_cfg.modules.django_twilio.simple_service import SimpleTwilioService
from django_cfg.modules.django_twilio.sms import SMSOTPService
from django_cfg.modules.django_twilio.unified import DjangoTwilioService, UnifiedOTPService

# Convenience functions
from django_cfg.modules.django_twilio.utils import (
    asend_email_otp,
    asend_sms_otp,
    asend_whatsapp_otp,
    averify_otp,
    send_email_otp,
    send_sms_otp,
    send_whatsapp_otp,
    verify_otp,
)
from django_cfg.modules.django_twilio.whatsapp import WhatsAppOTPService

# Simple messaging convenience functions
try:
    from django_cfg.modules.django_twilio.simple_service import send_sms, send_whatsapp
except ImportError:
    send_whatsapp = None
    send_sms = None


# Public API
__all__ = [
    # Configuration
    "TwilioConfig",

    # Services
    "DjangoTwilioService",
    "SimpleTwilioService",
    "WhatsAppOTPService",
    "EmailOTPService",
    "SMSOTPService",
    "UnifiedOTPService",
    "BaseTwilioService",

    # Exceptions
    "TwilioError",
    "TwilioConfigurationError",
    "TwilioVerificationError",
    "TwilioSendError",

    # OTP functions
    "send_whatsapp_otp",
    "send_email_otp",
    "send_sms_otp",
    "verify_otp",
    "asend_whatsapp_otp",
    "asend_email_otp",
    "asend_sms_otp",
    "averify_otp",

    # Utility functions
    "is_async_context",
]

# Add simple messaging if available
if send_whatsapp is not None:
    __all__.extend(["send_whatsapp", "send_sms"])
