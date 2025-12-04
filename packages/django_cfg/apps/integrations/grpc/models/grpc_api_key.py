"""
gRPC API Key Model.

Django model for managing API keys used for gRPC authentication.
"""

import secrets

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_api_key() -> str:
    """Generate a secure random API key (64 hex chars = 256 bits)."""
    return secrets.token_hex(32)


class GrpcApiKey(models.Model):
    """
    API Key for gRPC authentication.

    Example:
        >>> key = GrpcApiKey.objects.create(user=admin_user, name="Bot Service")
        >>> print(key.key)  # Use this in x-api-key header
    """

    from ..managers.grpc_api_key import GrpcApiKeyManager

    objects: GrpcApiKeyManager = GrpcApiKeyManager()

    # Identity
    key = models.CharField(
        max_length=64,
        unique=True,
        default=generate_api_key,
        db_index=True,
    )

    name = models.CharField(
        max_length=255,
        help_text="Descriptive name (e.g., 'Bot Service')",
    )

    description = models.TextField(blank=True)

    # User association
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grpc_api_keys",
    )

    # Status
    is_active = models.BooleanField(default=True, db_index=True)

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Null = never expires",
    )

    # Usage tracking
    last_used_at = models.DateTimeField(null=True, blank=True)
    request_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "django_cfg_grpc_api_key"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]
        verbose_name = "gRPC API Key"
        verbose_name_plural = "gRPC API Keys"

    def __str__(self) -> str:
        """String representation."""
        status = "✓" if self.is_valid else "✗"
        return f"{status} {self.name} ({self.user.username})"

    @property
    def is_expired(self) -> bool:
        """Check if key has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if key is valid (active and not expired)."""
        return self.is_active and not self.is_expired

    @property
    def masked_key(self) -> str:
        """Return masked version of key for display."""
        if len(self.key) <= 8:
            return self.key
        return f"{self.key[:4]}...{self.key[-4:]}"

    def mark_used(self) -> None:
        """Mark this key as used (update last_used_at and increment counter) (SYNC)."""
        self.last_used_at = timezone.now()
        self.request_count += 1
        self.save(update_fields=["last_used_at", "request_count"])

    async def amark_used(self) -> None:
        """Mark this key as used (update last_used_at and increment counter) (ASYNC - Django 5.2)."""
        self.last_used_at = timezone.now()
        self.request_count += 1
        await self.asave(update_fields=["last_used_at", "request_count"])

    def revoke(self) -> None:
        """Revoke this key (set is_active=False)."""
        self.is_active = False
        self.save(update_fields=["is_active"])


__all__ = ["GrpcApiKey", "generate_api_key"]
