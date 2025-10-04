"""
Base managers for knowbase models.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseKnowbaseManager(models.Manager):
    """Base manager with common functionality for knowbase models."""
    
    def for_user(self, user):
        """Explicitly filter by specific user."""
        return self.get_queryset().filter(user=user)
    
    def all_users(self):
        """Get unfiltered queryset (admin use)."""
        return self.get_queryset()
    
    def public(self):
        """Get public records (if model has is_public field)."""
        if hasattr(self.model, 'is_public'):
            return self.get_queryset().filter(is_public=True)
        return self.get_queryset()
    
    def active(self):
        """Get active records (if model has is_active field)."""
        if hasattr(self.model, 'is_active'):
            return self.get_queryset().filter(is_active=True)
        return self.get_queryset()
