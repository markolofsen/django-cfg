"""
Admin configuration for Accounts app.
"""

from .user import CustomUserAdmin
from .otp import OTPSecretAdmin
from .registration_source import RegistrationSourceAdmin, UserRegistrationSourceAdmin
from .profile import UserProfileAdmin
from .activity import UserActivityAdmin
from .group import GroupAdmin

__all__ = [
    'CustomUserAdmin',
    'OTPSecretAdmin', 
    'RegistrationSourceAdmin',
    'UserRegistrationSourceAdmin',
    'UserProfileAdmin',
    'UserActivityAdmin',
    'GroupAdmin',
]
