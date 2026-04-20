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


# Token-probe rate limit. The streaming password gate already caps
# bcrypt attempts at 5-fails/5-min (Redis `agent_pw_fails:{session_id}`);
# the unary guard had no equivalent, so an attacker holding a list of
# candidate tokens could test all of them with zero penalty. This cap
# is deliberately looser than the password one — token space is
# 256-bit so the realistic risk is log-scraping / hijacked-session
# replay, not brute force — but enough to make probing expensive and
# visible in ops dashboards.
_PROBE_FAILS_LIMIT = 30
_PROBE_FAILS_WINDOW_SECONDS = 5 * 60


def _probe_key(session_id: str) -> str:
    return f"grpc_session_probe_fails:{session_id}"


def record_token_probe_failure(session_id: str) -> int:
    """Bump the token-probe failure counter for a session.

    Returns the post-increment count. Callers compare it against
    ``PROBE_FAILS_LIMIT`` to decide whether to return RESOURCE_EXHAUSTED
    on top of the plain UNAUTHENTICATED. TTL on the key is refreshed
    on every increment so a slow drip never escapes the window.
    """
    from django.core.cache import cache

    key = _probe_key(session_id)
    try:
        current = cache.incr(key)
    except ValueError:
        # Key missing — first failure in the window. `incr` on a
        # missing key raises ValueError in django-redis; set to 1 and
        # set the TTL at the same time.
        cache.set(key, 1, timeout=_PROBE_FAILS_WINDOW_SECONDS)
        return 1
    # Refresh TTL so a sustained probe can't outrun the window by
    # pacing slower than 5 min between attempts.
    if hasattr(cache, "expire"):
        cache.expire(key, _PROBE_FAILS_WINDOW_SECONDS)
    return int(current)


def reset_token_probe_failures(session_id: str) -> None:
    """Clear the probe counter — called on a successful verify so a
    user who fumbled their first couple of tokens doesn't accumulate
    fails forever."""
    from django.core.cache import cache
    cache.delete(_probe_key(session_id))


def is_token_probing_locked(session_id: str) -> bool:
    """Check if a session is currently rate-limited for token probing."""
    from django.core.cache import cache
    count = cache.get(_probe_key(session_id)) or 0
    return int(count) >= _PROBE_FAILS_LIMIT


PROBE_FAILS_LIMIT = _PROBE_FAILS_LIMIT
PROBE_FAILS_WINDOW_SECONDS = _PROBE_FAILS_WINDOW_SECONDS


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


__all__ = [
    "issue_session_token",
    "verify_session_token",
    "revoke_session_tokens",
    "record_token_probe_failure",
    "reset_token_probe_failures",
    "is_token_probing_locked",
    "PROBE_FAILS_LIMIT",
    "PROBE_FAILS_WINDOW_SECONDS",
]
