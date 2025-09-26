"""
API Key models for the Universal Payment System v2.0.

Handles API key management and access control.
"""

import secrets
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from .base import UUIDTimestampedModel

User = get_user_model()


class APIKey(UUIDTimestampedModel):
    """
    API Key model for user authentication and access control.
    
    Provides secure API access with usage tracking and rate limiting.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="User who owns this API key"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Human-readable name for this API key"
    )
    
    key = models.CharField(
        max_length=64,
        unique=True,
        validators=[MinLengthValidator(32)],
        help_text="The actual API key (auto-generated)"
    )
    
    # Access control
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this API key is active"
    )
    
    # Usage tracking
    total_requests = models.PositiveIntegerField(
        default=0,
        help_text="Total number of requests made with this key"
    )
    
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this API key was last used"
    )
    
    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this API key expires (null = never expires)"
    )
    
    # IP restrictions
    allowed_ips = models.TextField(
        blank=True,
        help_text="Comma-separated list of allowed IP addresses (empty = any IP)"
    )
    
    # Manager
    from .managers.api_key_managers import APIKeyManager
    objects = APIKeyManager()
    
    class Meta:
        db_table = 'payments_api_keys'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Override save to generate API key."""
        if not self.key:
            self.key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate API key data."""
        if self.expires_at and self.expires_at <= timezone.now():
            raise ValidationError("Expiration time must be in the future")
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key."""
        return secrets.token_urlsafe(32)
    
    @property
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if API key is valid (active and not expired)."""
        return self.is_active and not self.is_expired
    
    @property
    def masked_key(self) -> str:
        """Get masked version of API key for display."""
        if len(self.key) < 8:
            return self.key
        return f"{self.key[:4]}...{self.key[-4:]}"
    
    @property
    def days_until_expiry(self) -> int:
        """Get days until expiration."""
        if not self.expires_at:
            return -1  # Never expires
        if self.is_expired:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)
    
    def is_ip_allowed(self, ip_address: str) -> bool:
        """
        Check if IP address is allowed to use this API key.
        
        Args:
            ip_address: IP address to check
        
        Returns:
            bool: True if IP is allowed
        """
        if not self.allowed_ips.strip():
            return True  # No restrictions
        
        allowed_list = [ip.strip() for ip in self.allowed_ips.split(',') if ip.strip()]
        return ip_address in allowed_list
    
    def increment_usage(self, ip_address: str = None):
        """Increment usage counter (delegates to manager)."""
        return self.__class__.objects.increment_api_key_usage(self, ip_address)
    
    def deactivate(self, reason: str = None):
        """Deactivate this API key (delegates to manager)."""
        return self.__class__.objects.deactivate_api_key(self, reason)
    
    def extend_expiry(self, days: int):
        """Extend API key expiration (delegates to manager)."""
        return self.__class__.objects.extend_api_key_expiry(self, days)
    
    @classmethod
    def create_for_user(cls, user, name="Default API Key", expires_in_days=None):
        """Create new API key for user (delegates to manager)."""
        return cls.objects.create_api_key_for_user(user, name, expires_in_days)
    
    @classmethod
    def get_valid_key(cls, key_value: str):
        """Get valid API key by key value (delegates to manager)."""
        return cls.objects.get_valid_api_key(key_value)
