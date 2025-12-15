"""
Push Subscription model - stores browser push subscriptions.

Simple model following django-cfg patterns (like CentrifugoLog).
"""

from django.conf import settings
from django.db import models


class PushSubscription(models.Model):
    """
    Web Push Subscription (VAPID protocol).

    Stores push subscription from browser's PushManager.subscribe().
    One user can have multiple subscriptions (different devices/browsers).
    """

    # User relationship
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        help_text='User owning this subscription'
    )

    # Subscription data (from browser)
    endpoint = models.URLField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text='Push service endpoint URL'
    )

    p256dh = models.CharField(
        max_length=255,
        help_text='P256DH encryption key (base64)'
    )

    auth = models.CharField(
        max_length=255,
        help_text='Auth secret (base64)'
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether subscription is active'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'django_cfg_push_subscription'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]
        verbose_name = 'Push Subscription'
        verbose_name_plural = 'Push Subscriptions'

    def __str__(self):
        return f'{self.user.username} - {self.endpoint[:50]}...'

    def to_webpush_dict(self):
        """Convert to pywebpush subscription format."""
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth
            }
        }


__all__ = ['PushSubscription']
