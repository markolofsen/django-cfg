"""
Manager for GrpcApiKey model.

Provides convenient methods for API key management.
"""

from datetime import timedelta
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class GrpcApiKeyManager(models.Manager):
    """
    Manager for GrpcApiKey model.

    Provides convenient methods for creating and validating API keys.
    """

    def create_for_user(
        self,
        user: User,
        name: str,
        description: str = "",
        expires_in_days: Optional[int] = None,
    ) -> "GrpcApiKey":
        """
        Create a new API key for a user.

        Args:
            user: User this key authenticates as
            name: Descriptive name for this key
            description: Additional details about this key
            expires_in_days: Number of days until expiration (None = never)

        Returns:
            Created GrpcApiKey instance

        Example:
            >>> key = GrpcApiKey.objects.create_for_user(
            ...     user=admin_user,
            ...     name="Analytics Service",
            ...     description="Internal analytics microservice",
            ...     expires_in_days=365,
            ... )
        """
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timedelta(days=expires_in_days)

        return self.create(
            user=user,
            name=name,
            description=description,
            expires_at=expires_at,
        )

    def get_by_key(self, key: str) -> Optional["GrpcApiKey"]:
        """
        Get API key by key string.

        Args:
            key: API key string

        Returns:
            GrpcApiKey instance or None if not found

        Example:
            >>> api_key = GrpcApiKey.objects.get_by_key("abc123...")
            >>> if api_key and api_key.is_valid:
            ...     user = api_key.user
        """
        try:
            return self.select_related("user").get(key=key)
        except self.model.DoesNotExist:
            return None

    def validate_key(self, key: str) -> Optional[User]:
        """
        Validate API key and return associated user.

        Args:
            key: API key string

        Returns:
            User instance if key is valid, None otherwise

        Example:
            >>> user = GrpcApiKey.objects.validate_key("abc123...")
            >>> if user:
            ...     print(f"Authenticated as {user.username}")
        """
        api_key = self.get_by_key(key)

        if not api_key:
            return None

        if not api_key.is_valid:
            return None

        # Mark as used
        api_key.mark_used()

        return api_key.user

    def active(self):
        """
        Get all active API keys.

        Returns:
            QuerySet of active keys

        Example:
            >>> active_keys = GrpcApiKey.objects.active()
        """
        return self.filter(is_active=True)

    def valid(self):
        """
        Get all valid API keys (active and not expired).

        Returns:
            QuerySet of valid keys

        Example:
            >>> valid_keys = GrpcApiKey.objects.valid()
        """
        now = timezone.now()
        return self.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        )

    def for_user(self, user: User):
        """
        Get all API keys for a user.

        Args:
            user: User instance

        Returns:
            QuerySet of keys for this user

        Example:
            >>> user_keys = GrpcApiKey.objects.for_user(request.user)
        """
        return self.filter(user=user)

    def expired(self):
        """
        Get all expired API keys.

        Returns:
            QuerySet of expired keys

        Example:
            >>> expired_keys = GrpcApiKey.objects.expired()
        """
        return self.filter(
            expires_at__isnull=False,
            expires_at__lte=timezone.now()
        )

    def revoke_all_for_user(self, user: User) -> int:
        """
        Revoke all API keys for a user.

        Args:
            user: User instance

        Returns:
            Number of keys revoked

        Example:
            >>> count = GrpcApiKey.objects.revoke_all_for_user(user)
            >>> print(f"Revoked {count} keys")
        """
        return self.filter(user=user, is_active=True).update(is_active=False)


__all__ = ["GrpcApiKeyManager"]
