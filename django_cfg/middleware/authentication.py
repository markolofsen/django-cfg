"""
Custom JWT Authentication for Django CFG.

Extends rest_framework_simplejwt.authentication.JWTAuthentication to automatically
update user's last_login field on successful authentication.

Also provides JWTAwareAuthenticationMixin for explicit use in project backends,
and patches DRF's Request._authenticate so that any extra authentication backend
automatically skips JWT tokens without requiring any changes in the project.
"""

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.request import Request as DRFRequest
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)

# JWT tokens always start with Base64url-encoded '{"' = 'eyJ'
_JWT_PREFIX = "eyJ"


def _bearer_is_jwt(request) -> bool:
    """Return True if the request carries a JWT Bearer token."""
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        return auth[7:].startswith(_JWT_PREFIX)
    return False


def _patch_drf_authenticate():
    """
    Monkey-patch DRF Request._authenticate once at import time.

    The patched version catches AuthenticationFailed raised by non-JWT backends
    when the request carries a JWT Bearer token, and continues to the next
    backend instead of propagating the error.  This lets projects register
    API-key backends in extra_authentication_classes without any changes to
    those backends — JWT logins just fall through to JWTAuthentication.
    """
    def _jwt_aware_authenticate(self):
        jwt_request = _bearer_is_jwt(self)
        for authenticator in self.authenticators:
            try:
                result = authenticator.authenticate(self)
            except exceptions.AuthenticationFailed:
                if jwt_request:
                    # This backend rejected a JWT token — skip it, try the next one
                    continue
                self._not_authenticated()
                raise
            except exceptions.APIException:
                self._not_authenticated()
                raise

            if result is not None:
                self._authenticator = authenticator
                self.user, self.auth = result
                return

        self._not_authenticated()

    DRFRequest._authenticate = _jwt_aware_authenticate  # type: ignore[method-assign]


# Apply the patch immediately when this module is imported.
# This module is always imported by DRF before the first request because
# 'django_cfg.middleware.authentication.JWTAuthenticationWithLastLogin' is in
# DEFAULT_AUTHENTICATION_CLASSES — DRF imports it on first authenticate() call.
# The patch is idempotent: re-running it is safe (replaces the same method again).
# DjangoCfgConfig.ready() also calls it for even earlier application.
_patch_drf_authenticate()


class JWTAwareAuthenticationMixin:
    """
    Optional explicit mixin for API-key backends.

    Not required when using django_cfg — the DRF patch above handles it
    automatically for all backends.  Kept for projects that want to be
    explicit or that don't use django_cfg's DRF integration.
    """

    JWT_PREFIX = _JWT_PREFIX

    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Bearer ") and auth[7:].startswith(self.JWT_PREFIX):
            return None
        return super().authenticate(request)  # type: ignore[misc]

User = get_user_model()


# Register OpenAPI extension for drf-spectacular
try:
    from drf_spectacular.extensions import OpenApiAuthenticationExtension

    class JWTAuthenticationWithLastLoginScheme(OpenApiAuthenticationExtension):
        """
        OpenAPI authentication scheme for JWTAuthenticationWithLastLogin.

        Registers the authentication scheme with drf-spectacular so it appears
        correctly in the generated OpenAPI schema.

        Uses unique name 'jwtAuthWithLastLogin' to avoid conflicts with
        standard rest_framework_simplejwt.authentication.JWTAuthentication.
        """
        target_class = 'django_cfg.middleware.authentication.JWTAuthenticationWithLastLogin'
        name = 'jwtAuthWithLastLogin'  # Unique name to avoid conflicts

        def get_security_definition(self, auto_schema):
            """Return JWT Bearer token security definition."""
            return {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }

except ImportError:
    # drf-spectacular not installed, skip extension registration
    pass


class JWTAuthenticationWithLastLogin(JWTAuthentication):
    """
    JWT Authentication that updates last_login on successful authentication.

    Updates last_login field with intelligent throttling to avoid database spam.
    Only updates if last_login is None or older than the configured interval.

    Features:
    - Automatic last_login tracking for all JWT-authenticated requests
    - Built-in throttling (default: 5 minutes) to minimize database writes
    - In-memory cache for tracking last update times
    - Automatic cache cleanup to prevent memory leaks
    - Error handling to prevent authentication failures

    Usage:
        Add to REST_FRAMEWORK settings:
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'django_cfg.apps.system.accounts.authentication.JWTAuthenticationWithLastLogin',
        ]
    """

    # Class-level cache to track last update times (shared across all instances)
    _last_updates = {}

    # Update interval in seconds (5 minutes by default, same as UserActivityMiddleware)
    UPDATE_INTERVAL = 300

    # Maximum cache size before cleanup (prevents memory leaks)
    MAX_CACHE_SIZE = 1000
    CLEANUP_CACHE_SIZE = 500

    def get_user(self, validated_token):
        """
        Override to check if user is active/not deleted.

        Simple JWT by default does NOT check is_active, so we add this check
        to ensure deleted/deactivated accounts cannot use existing tokens.

        Args:
            validated_token: Validated JWT token

        Returns:
            User instance if active, raises AuthenticationFailed otherwise
        """
        user = super().get_user(validated_token)

        # Check if user is active (is_active=False means deactivated or deleted)
        if not user.is_active:
            logger.warning(
                f"Authentication attempt with inactive/deleted account: "
                f"user_id={user.pk}, email={user.email}"
            )
            raise exceptions.AuthenticationFailed(
                'User account is deactivated or deleted.',
                code='user_inactive'
            )

        return user

    def authenticate(self, request):
        """
        Authenticate request and update last_login if needed.

        Args:
            request: Django HttpRequest object

        Returns:
            Tuple of (user, token) if authentication succeeds, None otherwise
        """
        # Perform standard JWT authentication
        result = super().authenticate(request)

        if result is not None:
            user, token = result
            # Update last_login with throttling
            self._update_last_login(user)

        return result

    def _update_last_login(self, user):
        """
        Update user's last_login field with intelligent throttling.

        Only updates if:
        - last_login is None (never logged in)
        - last_login is older than UPDATE_INTERVAL seconds

        Uses UPDATE query to avoid triggering signals and save() overhead.

        Args:
            user: User instance to update
        """
        now = timezone.now()
        user_id = user.pk

        # Check if we should update (avoid database spam)
        last_update = self._last_updates.get(user_id)
        if last_update and (now - last_update).total_seconds() < self.UPDATE_INTERVAL:
            # Skip update - too soon since last update
            return

        try:
            # Use update() to avoid triggering signals and save() overhead
            # This is more efficient than user.save(update_fields=['last_login'])
            updated_count = User.objects.filter(pk=user_id).update(last_login=now)

            if updated_count > 0:
                # Cache the update time
                self._last_updates[user_id] = now

                logger.debug(
                    f"Updated last_login for user {user.email} (ID: {user_id}) "
                    f"via JWT authentication"
                )

                # Clean up old cache entries to prevent memory leaks
                if len(self._last_updates) > self.MAX_CACHE_SIZE:
                    self._cleanup_cache()

        except Exception as e:
            # Log error but don't break authentication
            # Authentication should succeed even if last_login update fails
            logger.error(
                f"Failed to update last_login for user {user_id}: {e}",
                exc_info=True
            )

    def _cleanup_cache(self):
        """
        Clean up old cache entries to prevent memory leaks.

        Keeps only the most recent CLEANUP_CACHE_SIZE entries.
        Sorted by update time (newest first).
        """
        try:
            # Sort by update time (value), keep newest entries
            sorted_items = sorted(
                self._last_updates.items(),
                key=lambda x: x[1],
                reverse=True
            )

            # Keep only the most recent entries
            self._last_updates = dict(sorted_items[:self.CLEANUP_CACHE_SIZE])

            logger.debug(
                f"Cleaned up last_login cache: "
                f"kept {len(self._last_updates)} most recent entries"
            )

        except Exception as e:
            logger.error(f"Failed to cleanup last_login cache: {e}")

    @classmethod
    def get_cache_stats(cls):
        """
        Get cache statistics for monitoring/debugging.

        Returns:
            dict: Cache statistics including size and configuration
        """
        return {
            'cache_size': len(cls._last_updates),
            'max_cache_size': cls.MAX_CACHE_SIZE,
            'update_interval_seconds': cls.UPDATE_INTERVAL,
            'update_interval_minutes': cls.UPDATE_INTERVAL / 60,
        }
