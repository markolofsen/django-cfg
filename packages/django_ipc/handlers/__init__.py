"""
Built-in WebSocket Handlers.

Provides ready-to-use handlers for common WebSocket operations.

Example:
    >>> from django_ipc.handlers import (
    ...     BaseHandler,
    ...     NotificationHandler,
    ...     BroadcastHandler,
    ... )
"""

from .base import BaseHandler
from .notification import NotificationHandler
from .broadcast import BroadcastHandler

__all__ = [
    "BaseHandler",
    "NotificationHandler",
    "BroadcastHandler",
]
