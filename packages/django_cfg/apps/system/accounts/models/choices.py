"""
Model choices constants for accounts app.
"""

from django.db import models


class ActivityType(models.TextChoices):
    """User activity types."""
    LOGIN = 'login', 'Login'
    LOGOUT = 'logout', 'Logout'
    OTP_REQUESTED = 'otp_requested', 'OTP Requested'
    OTP_VERIFIED = 'otp_verified', 'OTP Verified'
    PROFILE_UPDATED = 'profile_updated', 'Profile Updated'
    REGISTRATION = 'registration', 'Registration'


class TwilioResponseType(models.TextChoices):
    """Twilio response types."""
    API_SEND = 'api_send', 'API Send Request'
    API_VERIFY = 'api_verify', 'API Verify Request'
    WEBHOOK_STATUS = 'webhook_status', 'Webhook Status Update'
    WEBHOOK_DELIVERY = 'webhook_delivery', 'Webhook Delivery Report'


class TwilioServiceType(models.TextChoices):
    """Twilio service types."""
    WHATSAPP = 'whatsapp', 'WhatsApp'
    SMS = 'sms', 'SMS'
    VOICE = 'voice', 'Voice'
    EMAIL = 'email', 'Email'
    VERIFY = 'verify', 'Verify API'
