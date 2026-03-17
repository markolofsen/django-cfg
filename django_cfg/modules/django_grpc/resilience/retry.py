"""
django_grpc.resilience.retry — Retry decorators for gRPC calls.

Provides production-grade retries with exponential backoff and jitter.
Uses stamina library if available; falls back to simple implementation.

Usage:
    @retry_grpc
    async def my_grpc_call():
        ...

    @with_retry(attempts=3, timeout=10.0)
    async def custom_retry():
        ...
"""

from __future__ import annotations

import logging
import random
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ParamSpec,
    TypeVar,
)

import grpc
import grpc.aio

# Conditional import for stamina
try:
    import stamina

    STAMINA_AVAILABLE = True
except ImportError:
    STAMINA_AVAILABLE = False
    stamina = None  # type: ignore

from ..config.constants import (
    GRPC_RETRY_BACKOFF_INITIAL_MS,
    GRPC_RETRY_BACKOFF_MAX_MS,
    GRPC_RETRY_BACKOFF_MULTIPLIER,
    get_max_retries,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")

# =============================================================================
# Retryable Status Codes
# =============================================================================

RETRYABLE_STATUS_CODES: frozenset[grpc.StatusCode] = frozenset(
    [
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.DEADLINE_EXCEEDED,
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        grpc.StatusCode.ABORTED,
        grpc.StatusCode.INTERNAL,  # Sometimes transient
    ]
)

NON_RETRYABLE_STATUS_CODES: frozenset[grpc.StatusCode] = frozenset(
    [
        grpc.StatusCode.INVALID_ARGUMENT,
        grpc.StatusCode.NOT_FOUND,
        grpc.StatusCode.PERMISSION_DENIED,
        grpc.StatusCode.UNAUTHENTICATED,
        grpc.StatusCode.CANCELLED,
        grpc.StatusCode.ALREADY_EXISTS,
        grpc.StatusCode.FAILED_PRECONDITION,
        grpc.StatusCode.OUT_OF_RANGE,
        grpc.StatusCode.UNIMPLEMENTED,
    ]
)


# =============================================================================
# Helper Functions
# =============================================================================


def is_retryable_error(exc: BaseException) -> bool:
    """Check if exception is retryable."""
    if isinstance(exc, grpc.aio.AioRpcError):
        return exc.code() in RETRYABLE_STATUS_CODES

    if isinstance(exc, grpc.RpcError):
        try:
            return exc.code() in RETRYABLE_STATUS_CODES
        except Exception:
            return False

    if isinstance(exc, (OSError, ConnectionError, TimeoutError)):
        return True

    return False


def _get_grpc_error_code(exc: BaseException) -> str:
    """Get gRPC error code from exception."""
    if isinstance(exc, grpc.aio.AioRpcError):
        return exc.code().name
    if isinstance(exc, grpc.RpcError):
        try:
            return exc.code().name
        except Exception:
            pass
    return type(exc).__name__


# =============================================================================
# Retry Decorators
# =============================================================================


def with_retry(
    attempts: int = 5,
    timeout: float = 30.0,
    wait_initial: float = 0.1,
    wait_max: float = 10.0,
    wait_jitter: float = 0.1,
    on: tuple[type[BaseException], ...] = (grpc.RpcError, grpc.aio.AioRpcError, OSError),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Configurable retry decorator with exponential backoff.

    Uses stamina library for production-grade retries.
    Falls back to simple retry if stamina not installed.
    """

    def should_retry(exc: BaseException) -> bool:
        if not isinstance(exc, on):
            return False
        return is_retryable_error(exc)

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        if STAMINA_AVAILABLE:
            @wraps(func)
            @stamina.retry(
                on=should_retry,
                attempts=attempts,
                timeout=timeout,
                wait_initial=wait_initial,
                wait_max=wait_max,
                wait_jitter=wait_jitter,
            )
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                return await func(*args, **kwargs)

            return wrapper
        else:
            import asyncio

            @wraps(func)
            async def fallback_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                last_exc: BaseException | None = None
                for attempt in range(attempts):
                    try:
                        return await func(*args, **kwargs)
                    except on as e:
                        last_exc = e
                        if not is_retryable_error(e) or attempt == attempts - 1:
                            raise
                        # B-2 fix: add full-jitter to avoid thundering herd.
                        # Pure exponential backoff without jitter causes all
                        # retrying callers to fire at the same moment after a
                        # transient outage. Full-jitter (random in [0, cap])
                        # spreads the retry wave across the whole window.
                        cap = min(wait_initial * (GRPC_RETRY_BACKOFF_MULTIPLIER**attempt), wait_max)
                        jitter_amount = random.uniform(0, wait_jitter) if wait_jitter > 0 else 0.0
                        wait = cap + jitter_amount
                        logger.warning(
                            f"Retry {attempt + 1}/{attempts} after "
                            f"{_get_grpc_error_code(e)}, waiting {wait:.2f}s"
                        )
                        await asyncio.sleep(wait)
                if last_exc:
                    raise last_exc
                raise RuntimeError("Unexpected retry loop exit")

            return fallback_wrapper

    return decorator


# =============================================================================
# Pre-configured Decorators
# =============================================================================

# Standard gRPC call retry: 5 attempts, 30s timeout
retry_grpc: Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]] = (
    with_retry(
        attempts=get_max_retries() or 5,
        timeout=30.0,
        wait_initial=GRPC_RETRY_BACKOFF_INITIAL_MS / 1000.0,
        wait_max=GRPC_RETRY_BACKOFF_MAX_MS / 1000.0,
        wait_jitter=0.1,
    )
)

# Connection establishment: 3 attempts, 10s timeout
retry_connection: Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]] = (
    with_retry(
        attempts=3,
        timeout=10.0,
        wait_initial=0.1,
        wait_max=2.0,
        wait_jitter=0.1,
        on=(grpc.RpcError, grpc.aio.AioRpcError, OSError, ConnectionError),
    )
)

# Streaming operations: 10 attempts, 60s timeout
retry_streaming: Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]] = (
    with_retry(
        attempts=10,
        timeout=60.0,
        wait_initial=0.5,
        wait_max=10.0,
        wait_jitter=0.2,
    )
)


__all__ = [
    "with_retry",
    "retry_grpc",
    "retry_connection",
    "retry_streaming",
    "is_retryable_error",
    "RETRYABLE_STATUS_CODES",
    "NON_RETRYABLE_STATUS_CODES",
]
