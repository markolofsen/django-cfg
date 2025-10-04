"""
Django CFG Accounts Models

This module provides all the models for the accounts app.
Models are organized by functionality:

- base: Base utilities and functions
- user: User model and related functionality  
- registration: Registration and source tracking models
- auth: Authentication models (OTP, etc.)
- activity: User activity tracking models
- integrations: Third-party integrations models (Twilio, etc.)
"""

# Import base utilities
from .base import user_avatar_path

# Import choices
from .choices import (
    ActivityType,
    TwilioResponseType,
    TwilioServiceType,
)

# Import user models
from .user import CustomUser

# Import registration models
from .registration import (
    RegistrationSource,
    UserRegistrationSource,
)

# Import authentication models
from .auth import OTPSecret

# Import activity models
from .activity import UserActivity

# Import integration models
from .integrations import TwilioResponse

# Export all models
__all__ = [
    # Base utilities
    'user_avatar_path',
    
    # Choices
    'ActivityType',
    'TwilioResponseType',
    'TwilioServiceType',
    
    # User models
    'CustomUser',
    
    # Registration models
    'RegistrationSource',
    'UserRegistrationSource',
    
    # Authentication models
    'OTPSecret',
    
    # Activity models
    'UserActivity',
    
    # Integration models
    'TwilioResponse',
]
