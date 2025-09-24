"""
Django CFG Middleware Package

Provides middleware components for Django CFG applications.
"""

from .user_activity import UserActivityMiddleware

__all__ = [
    'UserActivityMiddleware',
]
