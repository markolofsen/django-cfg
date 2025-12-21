"""
Django CFG Accounts Models

This module provides all the models for the accounts app.
Models are organized by functionality:

- base: Base utilities and functions
- user: User model and related functionality
- registration: Registration and source tracking models
- auth: Authentication models (OTP, etc.)
- activity: User activity tracking models
"""

# Import activity models
from .activity import UserActivity

# Import authentication models
from .auth import OTPSecret
from .base import user_avatar_path

# Import choices
from .choices import ActivityType

# Import OAuth models
from .oauth import OAuthConnection, OAuthProvider, OAuthState

# Import settings models
from .settings import TwoFactorEnforcement, TwoFactorSettings

# Import registration models
from .registration import (
    RegistrationSource,
    UserRegistrationSource,
)

# Import user models
from .user import CustomUser

# Export all models
__all__ = [
    # Base utilities
    'user_avatar_path',

    # Choices
    'ActivityType',

    # User models
    'CustomUser',

    # Registration models
    'RegistrationSource',
    'UserRegistrationSource',

    # Authentication models
    'OTPSecret',

    # Activity models
    'UserActivity',

    # OAuth models
    'OAuthConnection',
    'OAuthProvider',
    'OAuthState',

    # Settings models
    'TwoFactorEnforcement',
    'TwoFactorSettings',
]
