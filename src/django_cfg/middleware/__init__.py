"""
Django CFG Middleware Package

Provides middleware components for Django CFG applications.
"""

from .user_activity import UserActivityMiddleware
from .static_nocache import StaticNoCacheMiddleware

__all__ = [
    'UserActivityMiddleware',
    'StaticNoCacheMiddleware',
]
