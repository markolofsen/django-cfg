"""
Rate Limiting Decorators.

Universal rate limiting for Django views, DRF endpoints, and async RPC handlers.
Uses Redis for distributed rate limiting across multiple workers.

Example usage:
    # Django view
    @rate_limit(key='ip', rate='100/hour')
    def my_view(request):
        return JsonResponse({'success': True})

    # DRF ViewSet action
    @action(detail=True, methods=['post'])
    @rate_limit(key='user', rate='60/minute')
    def update_metrics(self, request, pk=None):
        ...

    # Async WebSocket RPC handler
    @websocket_rpc("ai_chat.send_message")
    @rate_limit(key='user', rate='20/minute')
    async def ai_chat_send_message(conn, params):
        ...
"""

import asyncio
import hashlib
import inspect
import logging
import time
from functools import wraps
from typing import Any, Callable, Literal, Optional, TypeVar, Union

from django.conf import settings
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)

# Rate limit key types
KeyType = Literal["ip", "user", "user_or_ip", "custom"]


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int = 0,
        remaining: int = 0,
        reset_in: int = 0,
    ):
        super().__init__(message)
        self.limit = limit
        self.remaining = remaining
        self.reset_in = reset_in


def _parse_rate(rate: str) -> tuple[int, int]:
    """
    Parse rate string into (limit, window_seconds).

    Args:
        rate: Rate string like "100/hour", "60/minute", "10/second"

    Returns:
        Tuple of (limit, window_in_seconds)

    Raises:
        ValueError: If rate format is invalid
    """
    try:
        limit_str, period = rate.split("/")
        limit = int(limit_str)

        # Convert period to seconds
        period_map = {
            "second": 1,
            "sec": 1,
            "s": 1,
            "minute": 60,
            "min": 60,
            "m": 60,
            "hour": 3600,
            "hr": 3600,
            "h": 3600,
            "day": 86400,
            "d": 86400,
        }

        window = period_map.get(period.lower())
        if window is None:
            raise ValueError(f"Unknown period: {period}")

        return limit, window

    except (ValueError, AttributeError) as e:
        raise ValueError(
            f"Invalid rate format '{rate}'. "
            "Expected format: 'limit/period' (e.g., '100/hour', '60/minute')"
        ) from e


def _get_cache_key(
    key_type: KeyType,
    request_or_conn: Any,
    method_name: str,
    custom_key: Optional[str] = None,
) -> str:
    """
    Generate cache key for rate limiting.

    Args:
        key_type: Type of key to use (ip, user, user_or_ip, custom)
        request_or_conn: Django request or WebSocket connection
        method_name: Name of the method being rate limited
        custom_key: Custom key value (required if key_type is 'custom')

    Returns:
        Cache key string
    """
    prefix = getattr(settings, 'RATE_LIMIT_KEY_PREFIX', 'ratelimit')

    # Determine the identifier based on key type
    if key_type == "custom":
        if not custom_key:
            raise ValueError("custom_key required when key_type='custom'")
        identifier = custom_key

    elif key_type == "ip":
        identifier = _get_client_ip(request_or_conn)

    elif key_type == "user":
        identifier = _get_user_id(request_or_conn)
        if not identifier:
            # Fall back to IP if user not authenticated
            identifier = f"anon:{_get_client_ip(request_or_conn)}"

    elif key_type == "user_or_ip":
        user_id = _get_user_id(request_or_conn)
        if user_id:
            identifier = f"user:{user_id}"
        else:
            identifier = f"ip:{_get_client_ip(request_or_conn)}"
    else:
        identifier = "unknown"

    # Hash the method name to keep key short
    method_hash = hashlib.md5(method_name.encode()).hexdigest()[:8]

    return f"{prefix}:{method_hash}:{identifier}"


def _get_client_ip(request_or_conn: Any) -> str:
    """Extract client IP from request or connection."""
    # Django HttpRequest
    if hasattr(request_or_conn, 'META'):
        x_forwarded_for = request_or_conn.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request_or_conn.META.get('REMOTE_ADDR', 'unknown')

    # WebSocket connection (Centrifugo)
    if hasattr(request_or_conn, 'client_ip'):
        return request_or_conn.client_ip or 'unknown'

    # DRF request
    if hasattr(request_or_conn, '_request'):
        return _get_client_ip(request_or_conn._request)

    return 'unknown'


def _get_user_id(request_or_conn: Any) -> Optional[str]:
    """Extract user ID from request or connection."""
    # WebSocket connection (Centrifugo) - has user_id directly
    if hasattr(request_or_conn, 'user_id'):
        return str(request_or_conn.user_id) if request_or_conn.user_id else None

    # Django HttpRequest
    if hasattr(request_or_conn, 'user'):
        user = request_or_conn.user
        if hasattr(user, 'is_authenticated') and user.is_authenticated:
            return str(user.pk)

    # DRF request
    if hasattr(request_or_conn, '_request'):
        return _get_user_id(request_or_conn._request)

    return None


def _get_redis_client():
    """Get Redis client from Django cache."""
    try:
        from django.core.cache import cache

        # Check if using django-redis
        if hasattr(cache, 'client'):
            return cache.client.get_client()

        # Try to get Redis client from default cache
        cache_backend = getattr(settings, 'CACHES', {}).get('default', {})
        if 'redis' in cache_backend.get('BACKEND', '').lower():
            return cache.client.get_client()

    except Exception as e:
        logger.warning(f"Could not get Redis client: {e}")

    return None


def _check_rate_limit_redis(
    redis_client,
    key: str,
    limit: int,
    window: int,
) -> tuple[bool, int, int]:
    """
    Check rate limit using Redis with sliding window.

    Args:
        redis_client: Redis client instance
        key: Cache key
        limit: Maximum requests allowed
        window: Time window in seconds

    Returns:
        Tuple of (allowed, remaining, reset_in_seconds)
    """
    now = time.time()
    window_start = now - window

    pipe = redis_client.pipeline()

    # Remove old entries outside the window
    pipe.zremrangebyscore(key, 0, window_start)

    # Count current requests in window
    pipe.zcard(key)

    # Add current request
    pipe.zadd(key, {str(now): now})

    # Set expiry on the key
    pipe.expire(key, window)

    results = pipe.execute()
    current_count = results[1]

    remaining = max(0, limit - current_count - 1)
    reset_in = int(window - (now - window_start))

    if current_count >= limit:
        return False, 0, reset_in

    return True, remaining, reset_in


def _check_rate_limit_memory(
    key: str,
    limit: int,
    window: int,
) -> tuple[bool, int, int]:
    """
    Check rate limit using in-memory storage (fallback).

    WARNING: This does not work across multiple workers.
    Use Redis in production.
    """
    from django.core.cache import cache

    now = time.time()
    cache_key = f"memory:{key}"

    # Get current state
    state = cache.get(cache_key, {'requests': [], 'window_start': now})

    # Filter requests within window
    window_start = now - window
    state['requests'] = [t for t in state['requests'] if t > window_start]

    current_count = len(state['requests'])
    remaining = max(0, limit - current_count - 1)
    reset_in = int(window - (now - window_start))

    if current_count >= limit:
        cache.set(cache_key, state, window)
        return False, 0, reset_in

    # Add current request
    state['requests'].append(now)
    cache.set(cache_key, state, window)

    return True, remaining, reset_in


def _check_rate_limit(
    key: str,
    limit: int,
    window: int,
) -> tuple[bool, int, int]:
    """
    Check rate limit using best available backend.

    Returns:
        Tuple of (allowed, remaining, reset_in_seconds)
    """
    redis_client = _get_redis_client()

    if redis_client:
        return _check_rate_limit_redis(redis_client, key, limit, window)
    else:
        logger.warning(
            "Redis not available for rate limiting. "
            "Using in-memory fallback (not suitable for production)."
        )
        return _check_rate_limit_memory(key, limit, window)


def _make_rate_limit_response(
    limit: int,
    remaining: int,
    reset_in: int,
) -> JsonResponse:
    """Create rate limit exceeded response."""
    response = JsonResponse(
        {
            "error": "Rate limit exceeded",
            "detail": f"Too many requests. Try again in {reset_in} seconds.",
            "retry_after": reset_in,
        },
        status=429,
    )

    # Add rate limit headers
    response["X-RateLimit-Limit"] = str(limit)
    response["X-RateLimit-Remaining"] = str(remaining)
    response["X-RateLimit-Reset"] = str(reset_in)
    response["Retry-After"] = str(reset_in)

    return response


def rate_limit(
    key: KeyType = "user_or_ip",
    rate: str = "100/hour",
    custom_key: Optional[str] = None,
    block: bool = True,
    on_exceed: Optional[Callable] = None,
) -> Callable[[F], F]:
    """
    Universal rate limiting decorator.

    Works with:
    - Django function-based views
    - Django class-based views
    - DRF ViewSet actions
    - Async WebSocket RPC handlers

    Args:
        key: Type of key to use for rate limiting:
            - "ip": Rate limit by IP address
            - "user": Rate limit by user ID (falls back to IP for anonymous)
            - "user_or_ip": Use user ID if authenticated, IP otherwise
            - "custom": Use custom_key parameter
        rate: Rate limit string (e.g., "100/hour", "60/minute", "10/second")
        custom_key: Custom key value (required if key="custom")
        block: If True, return 429 response when limit exceeded.
               If False, set request.rate_limited = True and continue.
        on_exceed: Optional callback when limit exceeded.
                   Called with (request_or_conn, limit, remaining, reset_in)

    Returns:
        Decorated function

    Example:
        @rate_limit(key='user', rate='20/minute')
        async def ai_chat_send_message(conn, params):
            ...

        @rate_limit(key='ip', rate='5/minute', block=True)
        def login_view(request):
            ...
    """
    limit, window = _parse_rate(rate)

    def decorator(func: F) -> F:
        # Determine if function is async
        is_async = asyncio.iscoroutinefunction(func)

        # Get function name for cache key
        func_name = f"{func.__module__}.{func.__qualname__}"

        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # First argument is usually request/conn
                request_or_conn = args[0] if args else None

                # Handle self for methods
                if request_or_conn and hasattr(request_or_conn, '__class__'):
                    if not (hasattr(request_or_conn, 'META') or
                            hasattr(request_or_conn, 'user_id')):
                        # This is 'self', request is second arg
                        request_or_conn = args[1] if len(args) > 1 else None

                if request_or_conn is None:
                    # Can't rate limit without request/conn
                    return await func(*args, **kwargs)

                # Generate cache key
                cache_key = _get_cache_key(
                    key, request_or_conn, func_name, custom_key
                )

                # Check rate limit
                allowed, remaining, reset_in = _check_rate_limit(
                    cache_key, limit, window
                )

                if not allowed:
                    logger.warning(
                        f"Rate limit exceeded for {func_name}: "
                        f"key={cache_key}, limit={limit}/{window}s"
                    )

                    if on_exceed:
                        on_exceed(request_or_conn, limit, remaining, reset_in)

                    if block:
                        raise RateLimitExceeded(
                            message="Rate limit exceeded",
                            limit=limit,
                            remaining=remaining,
                            reset_in=reset_in,
                        )
                    else:
                        # Mark as rate limited but continue
                        if hasattr(request_or_conn, '__dict__'):
                            request_or_conn.rate_limited = True
                            request_or_conn.rate_limit_info = {
                                'limit': limit,
                                'remaining': remaining,
                                'reset_in': reset_in,
                            }

                return await func(*args, **kwargs)

            return async_wrapper  # type: ignore

        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # First argument is usually request
                request = args[0] if args else None

                # Handle self for methods
                if request and hasattr(request, '__class__'):
                    if not hasattr(request, 'META'):
                        # This is 'self', request is second arg
                        request = args[1] if len(args) > 1 else None

                if request is None:
                    # Can't rate limit without request
                    return func(*args, **kwargs)

                # Generate cache key
                cache_key = _get_cache_key(
                    key, request, func_name, custom_key
                )

                # Check rate limit
                allowed, remaining, reset_in = _check_rate_limit(
                    cache_key, limit, window
                )

                if not allowed:
                    logger.warning(
                        f"Rate limit exceeded for {func_name}: "
                        f"key={cache_key}, limit={limit}/{window}s"
                    )

                    if on_exceed:
                        on_exceed(request, limit, remaining, reset_in)

                    if block:
                        return _make_rate_limit_response(limit, remaining, reset_in)
                    else:
                        # Mark as rate limited but continue
                        request.rate_limited = True
                        request.rate_limit_info = {
                            'limit': limit,
                            'remaining': remaining,
                            'reset_in': reset_in,
                        }

                # Add rate limit info to response headers
                response = func(*args, **kwargs)

                if hasattr(response, '__setitem__'):
                    response["X-RateLimit-Limit"] = str(limit)
                    response["X-RateLimit-Remaining"] = str(remaining)
                    response["X-RateLimit-Reset"] = str(reset_in)

                return response

            return sync_wrapper  # type: ignore

    return decorator


# Convenience aliases
ip_rate_limit = lambda rate: rate_limit(key="ip", rate=rate)
user_rate_limit = lambda rate: rate_limit(key="user", rate=rate)


__all__ = [
    "rate_limit",
    "ip_rate_limit",
    "user_rate_limit",
    "RateLimitExceeded",
]
