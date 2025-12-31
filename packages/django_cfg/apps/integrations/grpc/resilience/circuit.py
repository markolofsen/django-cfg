"""
Circuit breaker implementation using aiobreaker.

Provides per-target circuit breakers to prevent cascading failures.
Based on cmdop_sdk patterns.

Usage:
    # Get or create circuit breaker for target
    breaker = GRPCCircuitBreaker.get_or_create("service-name")

    # Check and execute
    if breaker.can_execute():
        try:
            result = await call_service()
            breaker.record_success()
        except Exception as e:
            breaker.record_failure(e)
            raise
    else:
        raise CircuitOpenError("service-name", breaker.time_until_retry())

    # Or use as decorator
    @breaker
    async def call_service():
        ...

Created: 2025-12-31
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from datetime import timezone as tz
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

# Conditional import for aiobreaker
try:
    from aiobreaker import CircuitBreaker, CircuitBreakerError, CircuitBreakerListener

    AIOBREAKER_AVAILABLE = True
except ImportError:
    AIOBREAKER_AVAILABLE = False
    CircuitBreaker = None  # type: ignore
    CircuitBreakerError = Exception  # type: ignore
    CircuitBreakerListener = object  # type: ignore

from ..configs.constants import (
    get_circuit_breaker_threshold,
    get_circuit_breaker_timeout,
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# Exceptions
# =============================================================================


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open and blocking calls."""

    def __init__(self, target_id: str, time_until_retry: float = 0):
        self.target_id = target_id
        self.time_until_retry = time_until_retry
        super().__init__(
            f"Circuit breaker open for '{target_id}', "
            f"retry in {time_until_retry:.1f}s"
        )


# =============================================================================
# Circuit State
# =============================================================================


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Blocking calls
    HALF_OPEN = "half_open"  # Testing recovery


# =============================================================================
# Listener for State Changes
# =============================================================================


class CircuitBreakerStateLogger(CircuitBreakerListener if AIOBREAKER_AVAILABLE else object):
    """Listener that logs circuit breaker state changes."""

    def state_change(self, breaker: Any, old_state: Any, new_state: Any) -> None:
        """Log state transitions."""
        # State objects have a .state property that returns the enum
        old_name = old_state.state.name if hasattr(old_state, "state") else str(old_state)
        new_name = new_state.state.name if hasattr(new_state, "state") else str(new_state)
        logger.warning(
            f"⚡ Circuit Breaker [{breaker.name}]: "
            f"{old_name} → {new_name} "
            f"(failures={breaker.fail_counter})"
        )


# =============================================================================
# Circuit Breaker Registry
# =============================================================================


class GRPCCircuitBreaker:
    """
    Circuit breaker for gRPC connections with per-target isolation.

    Uses aiobreaker library for production-grade circuit breaking.
    Falls back to simple implementation if aiobreaker not installed.

    States:
        CLOSED: Normal operation, failures counted
        OPEN: Failing fast, calls rejected immediately
        HALF_OPEN: Trial mode, testing if service recovered

    Usage:
        # Registry pattern - one breaker per target
        breaker = GRPCCircuitBreaker.get_or_create("agent-001")

        if breaker.can_execute():
            try:
                result = await stub.SendCommand(request)
                breaker.record_success()
            except grpc.aio.AioRpcError as e:
                breaker.record_failure(e)
                raise
        else:
            raise CircuitOpenError("agent-001")

        # Or use as decorator
        @breaker
        async def protected_call():
            return await stub.Method(request)
    """

    # Registry: one breaker per target
    _instances: Dict[str, "GRPCCircuitBreaker"] = {}
    _lock = asyncio.Lock()
    _state_logger = CircuitBreakerStateLogger()

    @classmethod
    async def get_or_create(
        cls,
        target_id: str,
        fail_max: Optional[int] = None,
        reset_timeout: Optional[float] = None,
        success_threshold: Optional[int] = None,
    ) -> "GRPCCircuitBreaker":
        """
        Get existing or create new circuit breaker for target.

        Args:
            target_id: Unique identifier for target (service/endpoint)
            fail_max: Failures before opening (default from config)
            reset_timeout: Seconds before trying half-open (default from config)
            success_threshold: Successes to close from half-open (default: 2)

        Returns:
            GRPCCircuitBreaker instance
        """
        async with cls._lock:
            if target_id not in cls._instances:
                cls._instances[target_id] = cls(
                    target_id=target_id,
                    fail_max=fail_max or get_circuit_breaker_threshold(),
                    reset_timeout=reset_timeout or get_circuit_breaker_timeout(),
                    success_threshold=success_threshold or CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
                )
            return cls._instances[target_id]

    @classmethod
    def get_or_create_sync(
        cls,
        target_id: str,
        fail_max: Optional[int] = None,
        reset_timeout: Optional[float] = None,
        success_threshold: Optional[int] = None,
    ) -> "GRPCCircuitBreaker":
        """Synchronous version for non-async contexts."""
        if target_id not in cls._instances:
            cls._instances[target_id] = cls(
                target_id=target_id,
                fail_max=fail_max or get_circuit_breaker_threshold(),
                reset_timeout=reset_timeout or get_circuit_breaker_timeout(),
                success_threshold=success_threshold or CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
            )
        return cls._instances[target_id]

    @classmethod
    def get(cls, target_id: str) -> Optional["GRPCCircuitBreaker"]:
        """Get existing circuit breaker or None."""
        return cls._instances.get(target_id)

    @classmethod
    async def remove(cls, target_id: str) -> bool:
        """Remove circuit breaker from registry."""
        async with cls._lock:
            if target_id in cls._instances:
                del cls._instances[target_id]
                return True
            return False

    @classmethod
    def remove_sync(cls, target_id: str) -> bool:
        """Synchronous remove."""
        if target_id in cls._instances:
            del cls._instances[target_id]
            return True
        return False

    @classmethod
    def get_all_stats(cls) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {target_id: cb.get_stats() for target_id, cb in cls._instances.items()}

    @classmethod
    async def reset_all(cls) -> int:
        """Reset all circuit breakers."""
        async with cls._lock:
            count = 0
            for breaker in cls._instances.values():
                breaker.reset()
                count += 1
            return count

    # =========================================================================
    # Instance Methods
    # =========================================================================

    def __init__(
        self,
        target_id: str,
        fail_max: int = 5,
        reset_timeout: float = 60.0,
        success_threshold: int = 2,
    ):
        """
        Initialize circuit breaker.

        Args:
            target_id: Unique identifier for target
            fail_max: Consecutive failures before opening circuit
            reset_timeout: Seconds to wait before trying half-open
            success_threshold: Successful calls to close from half-open
        """
        self.target_id = target_id
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.success_threshold = success_threshold

        # Use aiobreaker if available
        if AIOBREAKER_AVAILABLE:
            self._breaker = CircuitBreaker(
                fail_max=fail_max,
                timeout_duration=timedelta(seconds=reset_timeout),
                name=f"grpc_{target_id}",
                listeners=[self._state_logger],
            )
            self._use_aiobreaker = True
        else:
            # Fallback: simple implementation
            self._breaker = None
            self._use_aiobreaker = False
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at: Optional[datetime] = None
            self._total_calls = 0
            self._total_failures = 0
            self._total_blocked = 0
            self._last_failure_time: Optional[datetime] = None

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        if self._use_aiobreaker:
            state_name = self._breaker.current_state.name.lower()
            return CircuitState(state_name)
        return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking calls)."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def failure_count(self) -> int:
        """Get current consecutive failure count."""
        if self._use_aiobreaker:
            return self._breaker.fail_counter
        return self._failure_count

    def time_until_retry(self) -> float:
        """Get seconds until retry is allowed (for OPEN state)."""
        if self._use_aiobreaker:
            if self.state != CircuitState.OPEN:
                return 0.0
            # aiobreaker doesn't expose this directly, estimate based on timeout
            return self.reset_timeout
        else:
            if self._state != CircuitState.OPEN or self._opened_at is None:
                return 0.0
            elapsed = (datetime.now(tz.utc) - self._opened_at).total_seconds()
            return max(0.0, self.reset_timeout - elapsed)

    def can_execute(self) -> bool:
        """
        Check if call can be executed.

        Returns:
            True if call should proceed, False if blocked
        """
        if self._use_aiobreaker:
            # aiobreaker checks internally when decorated
            return not self.is_open
        else:
            # Simple implementation
            self._total_calls += 1

            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                if self._opened_at is None:
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True

                elapsed = (datetime.now(tz.utc) - self._opened_at).total_seconds()
                if elapsed >= self.reset_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
                    return True
                else:
                    self._total_blocked += 1
                    return False

            if self._state == CircuitState.HALF_OPEN:
                return True

            return False

    def record_success(self) -> None:
        """Record successful call."""
        if self._use_aiobreaker:
            # aiobreaker handles this automatically when using decorator
            pass
        else:
            if self._state == CircuitState.CLOSED:
                self._failure_count = 0
            elif self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.success_threshold:
                    self._transition_to(CircuitState.CLOSED)

    def record_failure(self, error: Optional[Exception] = None) -> None:
        """Record failed call."""
        if self._use_aiobreaker:
            # aiobreaker handles this automatically when using decorator
            pass
        else:
            self._total_failures += 1
            self._last_failure_time = datetime.now(tz.utc)

            if self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.fail_max:
                    self._transition_to(CircuitState.OPEN)
                    logger.warning(
                        f"⚡ Circuit OPEN for {self.target_id} after "
                        f"{self.fail_max} failures: {error}"
                    )

            elif self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to new state (fallback implementation)."""
        old_state = self._state
        if old_state == new_state:
            return

        self._state = new_state

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
            logger.info(f"⚡ Circuit CLOSED for {self.target_id}")

        elif new_state == CircuitState.OPEN:
            self._opened_at = datetime.now(tz.utc)
            self._success_count = 0
            logger.warning(f"⚡ Circuit OPEN for {self.target_id}")

        elif new_state == CircuitState.HALF_OPEN:
            self._failure_count = 0
            self._success_count = 0
            logger.info(f"⚡ Circuit HALF_OPEN for {self.target_id}")

    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        if self._use_aiobreaker:
            self._breaker.close()
        else:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
        logger.info(f"🔄 Circuit breaker reset for {self.target_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        if self._use_aiobreaker:
            return {
                "target_id": self.target_id,
                "state": self.state.value,
                "failure_count": self._breaker.fail_counter,
                "fail_max": self.fail_max,
                "reset_timeout": self.reset_timeout,
                "using_aiobreaker": True,
            }
        else:
            return {
                "target_id": self.target_id,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "fail_max": self.fail_max,
                "reset_timeout": self.reset_timeout,
                "total_calls": self._total_calls,
                "total_failures": self._total_failures,
                "total_blocked": self._total_blocked,
                "failure_rate": (
                    self._total_failures / self._total_calls
                    if self._total_calls > 0
                    else 0.0
                ),
                "last_failure_time": (
                    self._last_failure_time.isoformat() if self._last_failure_time else None
                ),
                "using_aiobreaker": False,
            }

    def __call__(
        self, func: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Use as decorator."""
        if self._use_aiobreaker:
            return self._breaker(func)
        else:
            # Fallback decorator
            from functools import wraps

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                if not self.can_execute():
                    raise CircuitOpenError(self.target_id, self.time_until_retry())
                try:
                    result = await func(*args, **kwargs)
                    self.record_success()
                    return result
                except Exception as e:
                    self.record_failure(e)
                    raise

            return wrapper


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "GRPCCircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "CircuitBreakerError",
    "AIOBREAKER_AVAILABLE",
]
