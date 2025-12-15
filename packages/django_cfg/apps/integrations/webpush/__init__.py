"""
Web Push Notifications integration for django-cfg.

Simple, functional push notification service using VAPID protocol.

Usage:
    from django_cfg.apps.integrations.webpush.services import send_push

    await send_push(user, title="Hello", body="Test notification")

Note: send_push and send_push_to_many are not imported here to avoid AppRegistryNotReady errors.
Import them directly from .services.push_service when needed.
"""

default_app_config = 'django_cfg.apps.integrations.webpush.apps.WebPushAppConfig'

__version__ = '1.0.0'
__all__ = []
