"""
gRPC API Key Model.

Django model for managing API keys used for gRPC authentication.
Provides secure, revocable authentication for services and CLI tools.
"""

import secrets
from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        32-character hex string (128 bits of entropy)
    """
    return secrets.token_hex(32)


class GrpcApiKey(models.Model):
    """
    API Key for gRPC authentication.

    Provides secure, revocable authentication for:
    - Service-to-service communication
    - CLI tools and scripts
    - Internal systems
    - Development and testing

    Features:
    - Auto-generated secure keys
    - User association for permissions
    - Expiration support
    - Usage tracking
    - Easy revocation via admin

    Example:
        >>> # Create API key for a service
        >>> key = GrpcApiKey.objects.create_for_user(
        ...     user=admin_user,
        ...     name="Analytics Service",
        ...     description="Internal analytics microservice"
        ... )
        >>> print(key.key)  # Use this in service config

        >>> # Check if key is valid
        >>> if key.is_valid:
        ...     user = key.user
    """

    # Custom manager
    from ..managers.grpc_api_key import GrpcApiKeyManager
    objects: GrpcApiKeyManager = GrpcApiKeyManager()

    class KeyTypeChoices(models.TextChoices):
        """Type of API key."""
        SERVICE = "service", "Service-to-Service"
        CLI = "cli", "CLI Tool"
        WEBHOOK = "webhook", "Webhook"
        INTERNAL = "internal", "Internal System"
        DEVELOPMENT = "development", "Development"

    # Identity
    key = models.CharField(
        max_length=64,
        unique=True,
        default=generate_api_key,
        db_index=True,
        help_text="API key (auto-generated)",
    )

    name = models.CharField(
        max_length=255,
        help_text="Descriptive name for this key (e.g., 'Analytics Service')",
    )

    description = models.TextField(
        blank=True,
        help_text="Additional details about this key's purpose",
    )

    key_type = models.CharField(
        max_length=20,
        choices=KeyTypeChoices.choices,
        default=KeyTypeChoices.SERVICE,
        help_text="Type of API key",
    )

    # User association
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="grpc_api_keys",
        help_text="User this key authenticates as",
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this key is currently active (can be used)",
    )

    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="When this key expires (null = never expires)",
    )

    # Usage tracking
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this key was last used",
    )

    request_count = models.IntegerField(
        default=0,
        help_text="Total number of requests made with this key",
    )

    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_grpc_api_keys",
        help_text="User who created this key",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this key was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this key was last updated",
    )

    class Meta:
        db_table = "django_cfg_grpc_api_key"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["is_active", "-created_at"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["key_type", "-created_at"]),
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
