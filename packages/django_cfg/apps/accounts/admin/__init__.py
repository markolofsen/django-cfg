"""
Accounts admin interfaces using Django Admin Utilities.

Modern, clean admin interfaces with Material Icons and consistent styling.
"""

from django.contrib import admin

# Import all admin classes
from .user_admin import CustomUserAdmin
from .activity_admin import UserActivityAdmin
from .otp_admin import OTPSecretAdmin
from .registration_admin import RegistrationSourceAdmin, UserRegistrationSourceAdmin
from .group_admin import GroupAdmin
from .twilio_admin import TwilioResponseAdmin, TwilioResponseInline

# All models are registered in their respective admin files using @admin.register
# This provides:
# - Clean separation of concerns
# - Material Icons integration
# - Type-safe configurations
# - Performance optimizations
# - Consistent styling with django_admin module

__all__ = [
    'CustomUserAdmin',
    'UserActivityAdmin',
    'OTPSecretAdmin',
    'RegistrationSourceAdmin',
    'UserRegistrationSourceAdmin',
    'GroupAdmin',
    'TwilioResponseAdmin',
    'TwilioResponseInline',
]
