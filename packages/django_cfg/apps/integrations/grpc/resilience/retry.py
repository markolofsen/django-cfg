"""
Retry decorators using stamina library.

Provides production-grade retries with exponential backoff and jitter.
Based on cmdop_sdk patterns.

Usage:
    @retry_grpc
    async def my_grpc_call():
        ...

    @with_retry(attempts=3, timeout=10.0)
    async def custom_retry():
        ...

Created: 2025-12-31
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    ParamSpec,
    Set,
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

from ..configs.constants import (
    get_max_retries,
    GRPC_RETRY_BACKOFF_INITIAL_MS,
    GRPC_RETRY_BACKOFF_MAX_MS,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")

# =============================================================================
# Retryable Status Codes
# =============================================================================

RETRYABLE_STATUS_CODES: Set[grpc.StatusCode] = frozenset(
    [
        grpc.StatusCode.UNAVAILABLE,
        grpc.StatusCode.DEADLINE_EXCEEDED,
        grpc.StatusCode.RESOURCE_EXHAUSTED,
        grpc.StatusCode.ABORTED,
        grpc.StatusCode.INTERNAL,  # Sometimes transient
    ]
)

NON_RETRYABLE_STATUS_CODES: Set[grpc.StatusCode] = frozenset(
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
    """
    Check if exception is retryable.

    Args:
        exc: Exception to check

    Returns:
        True if error should trigger retry
    """
    # gRPC async errors
    if isinstance(exc, grpc.aio.AioRpcError):
        return exc.code() in RETRYABLE_STATUS_CODES

    # gRPC sync errors
    if isinstance(exc, grpc.RpcError):
        try:
            return exc.code() in RETRYABLE_STATUS_CODES
        except Exception:
            return False

    # Network errors are usually retryable
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

    Args:
        attempts: Maximum retry attempts (default: 5)
        timeout: Total timeout in seconds (default: 30.0)
        wait_initial: Initial backoff wait in seconds (default: 0.1)
        wait_max: Maximum backoff wait in seconds (default: 10.0)
        wait_jitter: Jitter factor, e.g., 0.1 = 10% (default: 0.1)
        on: Exception types to retry on

    Returns:
        Decorator function

    Usage:
        @with_retry(attempts=3, timeout=10.0)
        async def my_grpc_call():
            ...
    """

    def should_retry(exc: BaseException) -> bool:
        """Backoff hook that checks both exception type and retryability."""
        # First check if it's one of the specified exception types
        if not isinstance(exc, on):
            return False
        # Then check if it's a retryable error (for gRPC-specific logic)
        return is_retryable_error(exc)

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        if STAMINA_AVAILABLE:
            # Use stamina for production-grade retries
            # The `on` parameter can be a backoff hook (callable that returns bool)
            @wraps(func)
            @stamina.retry(
                on=should_retry,  # Use combined backoff hook
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
            # Fallback: simple retry without exponential backoff
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
                        wait = min(wait_initial * (2**attempt), wait_max)
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


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "with_retry",
    "retry_grpc",
    "retry_connection",
    "retry_streaming",
    "is_retryable_error",
    "RETRYABLE_STATUS_CODES",
    "NON_RETRYABLE_STATUS_CODES",
]
