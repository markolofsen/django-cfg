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
