"""
Django CFG Middleware Package

Provides middleware components for Django CFG applications.
"""

from .user_activity import UserActivityMiddleware

# Import admin_notifications to register signal handlers
# This module contains Django signal receivers for admin login monitoring
# No middleware class needed - signals auto-register on import
from . import admin_notifications  # noqa: F401

__all__ = [
    'UserActivityMiddleware',
    'admin_notifications',
]
