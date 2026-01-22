"""
Key management for Django-CFG encryption.

Provides KeyManager for handling encryption key generation, caching, and rotation.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from .derivation import derive_key_pbkdf2, generate_salt

if TYPE_CHECKING:
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


class KeyManager:
    """
    Manages encryption keys for API response encryption.

    Keys are derived from Django's SECRET_KEY combined with optional
    user-specific or session-specific context for per-user key isolation.

    Features:
        - Key derivation from SECRET_KEY
        - Optional per-user key isolation
        - Optional per-session key isolation
        - In-memory caching for performance
        - Salt generation for client-side key derivation

    Example:
        ```python
        manager = KeyManager()

        # Get global key
        key = manager.get_encryption_key()

        # Get user-specific key
        key = manager.get_encryption_key(user_id=user.id)

        # Get key from request
        key = manager.get_key_for_request(request)
        ```
    """

    KEY_SIZE = 32  # 256 bits for AES-256
    SALT_SIZE = 16
    DEFAULT_ITERATIONS = 100_000
    CACHE_SIZE = 1000  # Max cached keys

    def __init__(
        self,
        iterations: int | None = None,
        key_prefix: str = "djangocfg_encryption",
    ):
        """
        Initialize KeyManager.

        Args:
            iterations: PBKDF2 iterations (default: 100,000)
            key_prefix: Prefix for key derivation salt
        """
        self.iterations = iterations or self.DEFAULT_ITERATIONS
        self.key_prefix = key_prefix
        self._key_cache: dict[str, bytes] = {}

    def get_encryption_key(
        self,
        user_id: int | str | None = None,
        session_id: str | None = None,
    ) -> bytes:
        """
        Get encryption key for the given context.

        Priority:
            1. Session-specific key (if session_id provided)
            2. User-specific key (if user_id provided)
            3. Global application key

        Args:
            user_id: Optional user ID for per-user key
            session_id: Optional session ID for per-session key

        Returns:
            32-byte encryption key
        """
        cache_key = self._build_cache_key(user_id, session_id)

        # Check cache
        if cache_key in self._key_cache:
            return self._key_cache[cache_key]

        # Derive key
        key = self._derive_key(user_id, session_id)

        # Cache with size limit
        if len(self._key_cache) >= self.CACHE_SIZE:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._key_cache.keys())[: self.CACHE_SIZE // 2]
            for k in keys_to_remove:
                del self._key_cache[k]

        self._key_cache[cache_key] = key
        return key

    def get_key_for_request(self, request: "HttpRequest") -> bytes:
        """
        Get encryption key for the current request.

        Extracts user_id from authenticated user if available.

        Args:
            request: Django HttpRequest

        Returns:
            Encryption key
        """
        user_id = None
        session_id = None

        # Get user ID if authenticated
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.id

        # Get session ID if available
        if hasattr(request, "session") and request.session.session_key:
            session_id = request.session.session_key

        return self.get_encryption_key(user_id=user_id, session_id=session_id)

    def generate_client_salt(self) -> bytes:
        """
        Generate salt to send to client for key derivation.

        The client can use this salt along with a shared secret
        to derive the same encryption key.

        Returns:
            Random 16-byte salt
        """
        return generate_salt(self.SALT_SIZE)

    def clear_cache(self) -> None:
        """Clear the key cache."""
        self._key_cache.clear()
        logger.debug("Encryption key cache cleared")

    def _build_cache_key(
        self,
        user_id: int | str | None,
        session_id: str | None,
    ) -> str:
        """Build cache key for key lookup."""
        if session_id:
            return f"session:{session_id}"
        if user_id:
            return f"user:{user_id}"
        return "global"

    def _derive_key(
        self,
        user_id: int | str | None,
        session_id: str | None,
    ) -> bytes:
        """
        Derive encryption key using PBKDF2.

        Key material:
            - Django SECRET_KEY (base)
            - User ID or Session ID (context)
            - Key prefix (application pepper)
        """
        from django.conf import settings

        # Base key material
        secret_key = settings.SECRET_KEY

        # Build salt from context
        salt_parts = [self.key_prefix]

        if session_id:
            salt_parts.append(f"session:{session_id}")
        elif user_id:
            salt_parts.append(f"user:{user_id}")
        else:
            salt_parts.append("global")

        # Create deterministic salt from context
        salt_input = ":".join(salt_parts).encode("utf-8")
        salt = hashlib.sha256(salt_input).digest()[: self.SALT_SIZE]

        return derive_key_pbkdf2(
            password=secret_key,
            salt=salt,
            iterations=self.iterations,
            key_length=self.KEY_SIZE,
        )


# Module-level singleton
_key_manager: Optional[KeyManager] = None


def get_key_manager() -> KeyManager:
    """
    Get the global KeyManager instance.

    Creates one if it doesn't exist.

    Returns:
        KeyManager singleton
    """
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager


def reset_key_manager() -> None:
    """Reset the global KeyManager instance."""
    global _key_manager
    if _key_manager is not None:
        _key_manager.clear_cache()
    _key_manager = None
