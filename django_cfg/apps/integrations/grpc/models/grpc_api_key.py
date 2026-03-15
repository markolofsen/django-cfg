"""
gRPC API Key Model.

Django model for managing API keys used for gRPC authentication.

Security:
    API keys are stored as SHA-256 hashes, not plaintext.
    The raw key is only shown once during creation.
"""

import hashlib
import secrets
from typing import Optional, TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


def generate_api_key() -> str:
    """Generate a secure random API key (64 hex chars = 256 bits)."""
    return secrets.token_hex(32)


def hash_api_key(raw_key: str) -> str:
    """
    Hash an API key using SHA-256.

    Args:
        raw_key: The raw API key string

    Returns:
        SHA-256 hash as hex string (64 chars)
    """
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


class GrpcApiKey(models.Model):
    """
    API Key for gRPC authentication.

    Security:
        - Keys are stored as SHA-256 hashes (key_hash field)
        - Only the prefix is stored for display (key_prefix field)
        - Raw key is shown only once during creation

    Migration Notes:
        - The `key` field is deprecated and will be removed
        - Use `key_hash` for validation
        - Use `key_prefix` for display

    Example:
        >>> # Create new key (returns raw key only once)
        >>> api_key, raw_key = GrpcApiKey.generate(user=admin_user, name="Bot Service")
        >>> print(raw_key)  # Save this! It won't be shown again

        >>> # Validate key
        >>> api_key = GrpcApiKey.validate_key(raw_key)
        >>> if api_key:
        ...     print(f"Valid key for user: {api_key.user}")
    """

    from ..managers.grpc_api_key import GrpcApiKeyManager

    objects: GrpcApiKeyManager = GrpcApiKeyManager()

    # =========================================================================
    # Key Storage (Secure)
    # =========================================================================

    # SHA-256 hash of the key (64 hex chars)
    key_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        null=True,  # Nullable for migration
        blank=True,
        help_text="SHA-256 hash of the API key",
    )

    # First 8 characters for display/identification
    key_prefix = models.CharField(
        max_length=8,
        db_index=True,
        null=True,  # Nullable for migration
        blank=True,
        help_text="First 8 characters of the key (for display only)",
    )

    # DEPRECATED: Plaintext key (to be removed after migration)
    # Keep for backward compatibility during migration period
    key = models.CharField(
        max_length=64,
        unique=True,
        default=generate_api_key,
        db_index=True,
        null=True,  # Make nullable for new keys
        blank=True,
        help_text="DEPRECATED: Use key_hash instead",
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
        # Prefer key_prefix if available (secure)
        if self.key_prefix:
            return f"{self.key_prefix}..."
        # Fallback to old key field during migration
        if self.key and len(self.key) > 8:
            return f"{self.key[:4]}...{self.key[-4:]}"
        return "***"

    @property
    def display_prefix(self) -> str:
        """Return key prefix for display (8 chars)."""
        if self.key_prefix:
            return self.key_prefix
        # Fallback during migration
        if self.key:
            return self.key[:8]
        return "********"

    # =========================================================================
    # Class Methods for Secure Key Management
    # =========================================================================

    @classmethod
    def generate(
        cls,
        user: "AbstractUser",
        name: str,
        description: str = "",
        expires_at: Optional[timezone.datetime] = None,
    ) -> tuple["GrpcApiKey", str]:
        """
        Generate a new API key securely.

        The raw key is returned only once and should be saved by the user.
        It cannot be retrieved later.

        Args:
            user: Django user who owns this key
            name: Descriptive name for the key
            description: Optional description
            expires_at: Optional expiration datetime

        Returns:
            Tuple of (GrpcApiKey instance, raw_key string)
            The raw_key is shown only once!

        Example:
            >>> api_key, raw_key = GrpcApiKey.generate(
            ...     user=admin_user,
            ...     name="Production Bot",
            ...     description="Bot service API key"
            ... )
            >>> print(f"Save this key: {raw_key}")  # Only chance to see it!
        """
        # Generate secure random key
        raw_key = generate_api_key()

        # Create instance with hash
        instance = cls(
            key_hash=hash_api_key(raw_key),
            key_prefix=raw_key[:8],
            key=None,  # Don't store plaintext
            user=user,
            name=name,
            description=description,
            expires_at=expires_at,
        )
        instance.save()

        return instance, raw_key

    @classmethod
    def validate_key(cls, raw_key: str) -> Optional["GrpcApiKey"]:
        """
        Validate an API key and return the instance if valid.

        Args:
            raw_key: The raw API key to validate

        Returns:
            GrpcApiKey instance if valid, None otherwise
        """
        if not raw_key:
            return None

        key_hash = hash_api_key(raw_key)

        try:
            # Try hash-based lookup first (new secure method)
            api_key = cls.objects.select_related("user").filter(
                key_hash=key_hash,
                is_active=True,
            ).first()

            if api_key and api_key.is_valid:
                return api_key

            # Fallback to plaintext lookup (for migration period)
            api_key = cls.objects.select_related("user").filter(
                key=raw_key,
                is_active=True,
            ).first()

            if api_key and api_key.is_valid:
                # Auto-migrate: add hash if missing
                if not api_key.key_hash:
                    api_key.key_hash = key_hash
                    api_key.key_prefix = raw_key[:8]
                    api_key.save(update_fields=["key_hash", "key_prefix"])
                return api_key

            return None

        except Exception:
            return None

    @classmethod
    async def avalidate_key(cls, raw_key: str) -> Optional["GrpcApiKey"]:
        """
        Validate an API key asynchronously (Django 5.2+).

        Args:
            raw_key: The raw API key to validate

        Returns:
            GrpcApiKey instance if valid, None otherwise
        """
        if not raw_key:
            return None

        key_hash = hash_api_key(raw_key)

        try:
            # Try hash-based lookup first (new secure method)
            api_key = await cls.objects.select_related("user").filter(
                key_hash=key_hash,
                is_active=True,
            ).afirst()

            if api_key and api_key.is_valid:
                return api_key

            # Fallback to plaintext lookup (for migration period)
            api_key = await cls.objects.select_related("user").filter(
                key=raw_key,
                is_active=True,
            ).afirst()

            if api_key and api_key.is_valid:
                # Auto-migrate: add hash if missing
                if not api_key.key_hash:
                    api_key.key_hash = key_hash
                    api_key.key_prefix = raw_key[:8]
                    await api_key.asave(update_fields=["key_hash", "key_prefix"])
                return api_key

            return None

        except Exception:
            return None

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


__all__ = ["GrpcApiKey", "generate_api_key", "hash_api_key"]
