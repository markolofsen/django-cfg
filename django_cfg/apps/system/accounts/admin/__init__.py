"""
Accounts admin interfaces using Django Admin Utilities.

Modern, clean admin interfaces with Material Icons and consistent styling.
"""

from django.contrib import admin
from django.contrib.auth.models import Group

from .activity_admin import UserActivityAdmin
from .group_admin import GroupAdmin
from .oauth_admin import OAuthConnectionAdmin, OAuthStateAdmin
from .otp_admin import OTPSecretAdmin
from .registration_admin import RegistrationSourceAdmin, UserRegistrationSourceAdmin

# Import all admin classes
from .user_admin import CustomUserAdmin

# Re-register Group with our custom admin (replaces Django's default)
# This needs to be in a ready() method or use try/except because Django's auth
# admin might register it first
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
admin.site.register(Group, GroupAdmin)

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
    'OAuthConnectionAdmin',
    'OAuthStateAdmin',
]
