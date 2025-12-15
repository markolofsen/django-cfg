"""
Web Push service layer.

Exports:
- send_push, send_push_to_many - Main service functions
- Pydantic models - Type-safe data structures
- Custom exceptions - Specific error types
"""

from .exceptions import (
    WebPushConfigurationError,
    WebPushDeliveryError,
    WebPushError,
    WebPushSubscriptionError,
)
from .models import BulkPushResult, PushPayload, PushResult, VapidConfig
from .push_service import send_push, send_push_to_many

__all__ = [
    # Main functions
    "send_push",
    "send_push_to_many",
    # Pydantic models
    "PushPayload",
    "VapidConfig",
    "PushResult",
    "BulkPushResult",
    # Exceptions
    "WebPushError",
    "WebPushConfigurationError",
    "WebPushSubscriptionError",
    "WebPushDeliveryError",
]
