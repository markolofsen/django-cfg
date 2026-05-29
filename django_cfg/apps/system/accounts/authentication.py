"""
API Key Authentication for Django CFG Accounts.

Provides DRF authentication via X-API-Key header.
Falls through (returns None) for requests without the header
or for views with AllowAny permission (public endpoints like OTP, OAuth).
"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import authentication, exceptions

logger = logging.getLogger(__name__)
User = get_user_model()


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using X-API-Key header.

    Header format:
        X-API-Key: <uuid>

    Behavior:
    - If X-API-Key header is missing → returns None (falls through to JWT)
    - If view has AllowAny permission → returns None (skip for public endpoints)
    - If key is invalid/expired → raises AuthenticationFailed
    - If user is inactive/deleted → raises AuthenticationFailed
    """

    keyword = "X-API-Key"

    def authenticate_header(self, request):
        """Return a value for the WWW-Authenticate header.

        DRF only emits 401 (rather than 403) for an unauthenticated request when
        the first authenticator defines this. Without it, any view that falls
        back to this authenticator first returns 403 for missing credentials.
        """
        return self.keyword

    def authenticate(self, request):
        key = self._extract_key(request)
        if not key:
            return None

        # Skip API key auth for public (AllowAny) endpoints
        if self._is_public_endpoint(request):
            return None

        return self._authenticate_credentials(request, key)

    def _extract_key(self, request):
        """Extract API key from X-API-Key header."""
        return request.META.get("HTTP_X_API_KEY", "")

    def _is_public_endpoint(self, request):
        """
        Check if the current view allows anonymous access.

        DRF passes the view instance as request._request._django_view or
        via the DRF request's authenticators. We check the view's
        permission classes to detect AllowAny.
        """
        # DRF sets the view on the request during dispatch
        view = getattr(request, "_request", None)
        if view is not None:
            view = getattr(view, "_django_view", None)
        if view is None:
            # Fallback: try to get from DRF request directly
            view = getattr(request, "parser_context", {}).get("view", None)
        if view is None:
            return False

        perms = getattr(view, "permission_classes", [])
        from rest_framework.permissions import AllowAny

        return any(
            issubclass(p, AllowAny) for p in perms if isinstance(p, type)
        )

    def _authenticate_credentials(self, request, key):
        """Validate API key and return (user, key_instance)."""
        from .models.api_key import UserAPIKey

        try:
            api_key = UserAPIKey.objects.select_related("user").get(key=key)
        except (UserAPIKey.DoesNotExist, ValueError, ValidationError):
            # ValueError / ValidationError: key is not a well-formed UUID, so it
            # can never match — treat the same as a missing key (invalid auth),
            # not an unhandled 500.
            logger.warning("API key authentication failed: invalid key")
            raise exceptions.AuthenticationFailed("Invalid API key.")

        user = api_key.user

        # Check user is active and not soft-deleted
        if not user.is_active or user.is_deleted:
            logger.warning(
                f"API key authentication failed: inactive/deleted user "
                f"user_id={user.pk}, email={user.email}"
            )
            raise exceptions.AuthenticationFailed(
                "User account is deactivated or deleted.",
                code="user_inactive",
            )

        logger.debug(f"API key authentication succeeded for user {user.email}")
        return (user, api_key)
