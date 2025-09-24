"""
API key managers.
"""

from django.db import models
from django.utils import timezone


class APIKeyManager(models.Manager):
    """Manager for APIKey model."""
    
    def get_active_keys(self, user=None):
        """Get active API keys."""
        queryset = self.filter(is_active=True)
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_expired_keys(self):
        """Get expired API keys."""
        return self.filter(
            expires_at__lte=timezone.now()
        )
    
    def get_valid_keys(self, user=None):
        """Get valid (active and not expired) API keys."""
        now = timezone.now()
        queryset = self.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset
