"""
API key models for the universal payments system.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .base import UUIDTimestampedModel

User = get_user_model()


class APIKey(UUIDTimestampedModel):
    """API keys for authentication and usage tracking."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="API key owner"
    )
    
    # Key details
    name = models.CharField(
        max_length=100,
        help_text="Human-readable key name"
    )
    key_value = models.CharField(
        max_length=255,
        unique=True,
        help_text="API key value (plain text)"
    )
    key_prefix = models.CharField(
        max_length=20,
        help_text="Key prefix for identification"
    )
    
    # Permissions
    is_active = models.BooleanField(
        default=True,
        help_text="Is key active"
    )
    
    # Usage tracking
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last usage timestamp"
    )
    usage_count = models.PositiveBigIntegerField(
        default=0,
        help_text="Total usage count"
    )
    
    # Lifecycle
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Key expiration"
    )
    
    # Import and assign manager
    from ..managers import APIKeyManager
    objects = APIKeyManager()
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['key_value']),
            models.Index(fields=['key_prefix']),
            models.Index(fields=['last_used']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"API Key: {self.name} ({self.key_prefix}***)"
    
    def is_valid(self) -> bool:
        """Check if API key is valid."""
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at <= timezone.now():
            return False
        
        return True
    
    def record_usage(self):
        """Record API key usage."""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])
