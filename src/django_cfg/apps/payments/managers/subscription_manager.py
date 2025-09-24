"""
Subscription managers.
"""

from django.db import models
from django.utils import timezone


class SubscriptionManager(models.Manager):
    """Manager for Subscription model."""
    
    def get_active_subscriptions(self, user=None):
        """Get active subscriptions."""
        queryset = self.filter(
            status='active',
            expires_at__gt=timezone.now()
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset
    
    def get_expired_subscriptions(self, user=None):
        """Get expired subscriptions."""
        queryset = self.filter(
            expires_at__lte=timezone.now()
        )
        if user:
            queryset = queryset.filter(user=user)
        return queryset


class EndpointGroupManager(models.Manager):
    """Manager for EndpointGroup model."""
    
    def get_active_groups(self):
        """Get active endpoint groups."""
        return self.filter(is_active=True)
