"""
django_grpc.resilience.circuit — Circuit breaker for gRPC connections.

Per-target circuit breakers to prevent cascading failures.
Uses aiobreaker for production-grade async circuit breaking.

Usage:
    # Get or create circuit breaker for target
    breaker = GRPCCircuitBreaker.get_or_create_sync("service-name")

    if breaker.can_execute():
        try:
            result = await stub.Method(request)
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
"""

from __future__ import annotations

import asyncio
import logging
import threading
from datetime import timedelta
from typing import Any, Callable, Dict, Optional, TypeVar

from aiobreaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerListener,
)

from ..config.constants import (
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD,
    get_circuit_breaker_threshold,
    get_circuit_breaker_timeout,
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


from enum import Enum


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking calls
    HALF_OPEN = "half_open"  # Testing recovery


# =============================================================================
# Listener for State Changes
# =============================================================================


class CircuitBreakerStateLogger(CircuitBreakerListener):
    """Listener that logs circuit breaker state changes."""

    def state_change(self, breaker: Any, old: Any, new: Any) -> None:
        old_name = old.state.name if hasattr(old, "state") else str(old)
        new_name = new.state.name if hasattr(new, "state") else str(new)
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
    """

    # Registry: one breaker per target.
    # _sync_lock guards get_or_create_sync() — threading.Lock because that
    # method is called from sync contexts (e.g. pool creation at import time).
    # B-1 fix: without this lock two threads can simultaneously pass the
    # `target_id not in cls._instances` check and both create an instance;
    # the second write silently resets the failure counter of the first.
    _instances: Dict[str, "GRPCCircuitBreaker"] = {}
    _lock = asyncio.Lock()              # async paths (get_or_create, reset_all)
    _sync_lock = threading.Lock()       # sync path (get_or_create_sync)
    _state_logger = CircuitBreakerStateLogger()

    @classmethod
    async def get_or_create(
        cls,
        target_id: str,
        fail_max: Optional[int] = None,
        reset_timeout: Optional[float] = None,
        success_threshold: Optional[int] = None,
    ) -> "GRPCCircuitBreaker":
        """Get existing or create new circuit breaker for target."""
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
        """Synchronous version for non-async contexts.

        B-1 fix: guarded by _sync_lock to prevent a race where two threads
        simultaneously pass the membership check and one silently overwrites
        the other's instance (resetting its failure counter).
        """
        with cls._sync_lock:
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
        self.target_id = target_id
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.success_threshold = success_threshold

        self._breaker = CircuitBreaker(
            fail_max=fail_max,
            timeout_duration=timedelta(seconds=reset_timeout),
            name=f"grpc_{target_id}",
            listeners=[self._state_logger],
        )

    @property
    def state(self) -> CircuitState:
        state_name = self._breaker.current_state.name.lower()
        return CircuitState(state_name)

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED

    @property
    def failure_count(self) -> int:
        return self._breaker.fail_counter

    def time_until_retry(self) -> float:
        if self.state != CircuitState.OPEN:
            return 0.0
        return self.reset_timeout

    def can_execute(self) -> bool:
        return not self.is_open

    def record_success(self) -> None:
        pass  # aiobreaker handles this via decorator

    def record_failure(self, error: Optional[Exception] = None) -> None:
        pass  # aiobreaker handles this via decorator

    def reset(self) -> None:
        self._breaker.close()
        logger.info(f"🔄 Circuit breaker reset for {self.target_id}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "state": self.state.value,
            "failure_count": self._breaker.fail_counter,
            "fail_max": self.fail_max,
            "reset_timeout": self.reset_timeout,
        }

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Use as decorator."""
        return self._breaker(func)


__all__ = [
    "GRPCCircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "CircuitBreakerError",
]
