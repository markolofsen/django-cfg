"""
Payment Background Tasks

Minimal task infrastructure for webhook processing using existing Dramatiq setup.
Uses django-cfg task configuration from knowbase module.
"""

from .webhook_processing import process_webhook_async

__all__ = [
    'process_webhook_async',
]
