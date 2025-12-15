"""
Custom exceptions for Web Push service.

Specific exception hierarchy following CRITICAL_REQUIREMENTS.md standards.
"""

from typing import Optional


class WebPushError(Exception):
    """
    Base exception for Web Push errors.

    All Web Push related exceptions should inherit from this.
    """

    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class WebPushConfigurationError(WebPushError):
    """VAPID configuration is missing or invalid."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message, code="WEBPUSH_CONFIG_ERROR", details=details
        )


class WebPushSubscriptionError(WebPushError):
    """Subscription not found or invalid."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message, code="WEBPUSH_SUBSCRIPTION_ERROR", details=details
        )


class WebPushDeliveryError(WebPushError):
    """Failed to deliver push notification."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message, code="WEBPUSH_DELIVERY_ERROR", details=details
        )


__all__ = [
    "WebPushError",
    "WebPushConfigurationError",
    "WebPushSubscriptionError",
    "WebPushDeliveryError",
]
