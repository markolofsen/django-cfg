"""
django_grpc.services.auth.session_token — Redis-backed session access tokens.

External callers authenticate to a session via password, then receive a
short-lived token. The token is sent as ``x-session-token`` metadata on
subsequent gRPC calls.

Internal callers (Django REST → gRPC) bypass this via ``x-internal-secret``.
"""

from __future__ import annotations

import logging
import secrets

logger = logging.getLogger(__name__)


def _get_ttl() -> int:
    """Read session_token_ttl from grpc auth config, fallback to 86400."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import settings as grpc_settings
        return grpc_settings.auth.session_token_ttl
    except Exception:
        return 86400


def _cache_key(session_id: str, token: str) -> str:
    return f"grpc_session_token:{session_id}:{token}"


def issue_session_token(session_id: str, ttl: int | None = None) -> str:
    """Issue a session access token after password verification.

    Returns the token string. Stored in Django cache (Redis).
    """
    from django.core.cache import cache

    if ttl is None:
        ttl = _get_ttl()
    token = secrets.token_urlsafe(32)
    cache.set(_cache_key(session_id, token), True, timeout=ttl)
    logger.debug("Issued session token for session=%s ttl=%d", session_id, ttl)
    return token


def verify_session_token(session_id: str, token: str) -> bool:
    """Verify a session access token from ``x-session-token`` metadata."""
    if not token:
        return False
    from django.core.cache import cache
    return bool(cache.get(_cache_key(session_id, token)))


def revoke_session_tokens(session_id: str) -> None:
    """Revoke all tokens for a session (e.g. on disconnect or password change).

    Uses Redis SCAN to find and delete matching keys.
    Falls back to Django cache delete_pattern if available (django-redis),
    otherwise logs a warning.
    """
    from django.core.cache import cache

    pattern = f"grpc_session_token:{session_id}:*"
    # django-redis exposes delete_pattern
    if hasattr(cache, "delete_pattern"):
        deleted = cache.delete_pattern(pattern)
        logger.debug("Revoked %s session tokens for session=%s", deleted, session_id)
    else:
        logger.warning(
            "Cannot bulk-revoke session tokens (cache backend lacks delete_pattern). "
            "Tokens for session=%s will expire naturally.",
            session_id,
        )


__all__ = ["issue_session_token", "verify_session_token", "revoke_session_tokens"]
