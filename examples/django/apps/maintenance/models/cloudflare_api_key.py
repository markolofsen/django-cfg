"""
CloudflareApiKey model.

Store Cloudflare API keys for different accounts/domains.
"""

from django.db import models
from django.core.exceptions import ValidationError


class CloudflareApiKey(models.Model):
    """
    Store Cloudflare API keys for different domains/accounts.
    
    Allows managing multiple Cloudflare accounts with different API tokens.
    """
    
    # Basic info
    name = models.CharField(
        max_length=100,
        help_text="Friendly name for this API key (e.g., 'Production', 'Staging')"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of what this key is used for"
    )
    
    # Cloudflare credentials
    api_token = models.CharField(
        max_length=255,
        help_text="Cloudflare API token"
    )
    account_id = models.CharField(
        max_length=32,
        blank=True,
        help_text="Cloudflare Account ID (auto-discovered if empty)"
    )
    
    # Settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this API key is active"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is the default API key to use"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this API key was last used"
    )
    
    class Meta:
        ordering = ['-is_default', 'name']
        verbose_name = "Cloudflare API Key"
        verbose_name_plural = "Cloudflare API Keys"
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_default']),
        ]
    
    def __str__(self) -> str:
        status = "🔑" if self.is_active else "🔒"
        default = " (Default)" if self.is_default else ""
        return f"{status} {self.name}{default}"
    
    def clean(self) -> None:
        """Validate model data."""
        super().clean()
        
        # Validate API token format (basic check)
        if not self.api_token.strip():
            raise ValidationError({'api_token': 'API token cannot be empty'})
        
        # Validate account_id format if provided
        if self.account_id and len(self.account_id) != 32:
            raise ValidationError({'account_id': 'Account ID must be 32 characters'})
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one default key."""
        if self.is_default:
            # Set all other keys to non-default
            self.__class__.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default(cls):
        """Get the default API key."""
        try:
            return cls.objects.filter(is_active=True, is_default=True).first()
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_active_keys(cls):
        """Get all active API keys."""
        return cls.objects.filter(is_active=True)
    
    def mark_used(self):
        """Mark this key as recently used."""
        from django.utils import timezone
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
