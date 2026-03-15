"""
Centrifugo resilience layer for auto-publishing.

Simple circuit breaker pattern without external dependencies.
Designed for non-critical auto-publishing use case.

Created: 2025-11-14
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

import logging
from datetime import datetime, timedelta, timezone as tz
from typing import Optional
from enum import Enum

# Logger will be configured by BidirectionalStreamingService via setup_streaming_logger
logger = logging.getLogger("grpc_streaming.circuit_breaker")


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Too many errors, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CentrifugoCircuitBreaker:
    """
    Simple circuit breaker for Centrifugo auto-publishing.

    **States**:
    - CLOSED: Normal operation, all calls go through
    - OPEN: Too many failures, all calls blocked
    - HALF_OPEN: Testing recovery, limited calls allowed

    **Configuration**:
    - failure_threshold: Max consecutive failures before opening (default: 5)
    - recovery_timeout: Seconds to wait before testing recovery (default: 60)
    - success_threshold: Successful calls needed to close from half-open (default: 2)

    **Usage**:
    ```python
    circuit = CentrifugoCircuitBreaker(failure_threshold=5, recovery_timeout=60)

    if circuit.can_execute():
        try:
            await publish_to_centrifugo(data)
            circuit.record_success()
        except Exception as e:
            circuit.record_failure(e)
    else:
        # Circuit is open, skip publishing
        pass
    ```

    **Thread Safety**: Not thread-safe, designed for single asyncio event loop.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2,
        enable_logging: bool = True,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Max consecutive failures before opening circuit
            recovery_timeout: Seconds to wait in OPEN state before trying HALF_OPEN
            success_threshold: Successful calls needed in HALF_OPEN to close circuit
            enable_logging: Enable state transition logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.enable_logging = enable_logging

        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None

        # Statistics
        self._total_calls = 0
        self._total_failures = 0
        self._total_blocked = 0

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking calls)."""
        return self._state == CircuitState.OPEN

    def can_execute(self) -> bool:
        """
        Check if call can be executed.

        Returns:
            True if call should proceed, False if blocked by circuit breaker
        """
        self._total_calls += 1

        # CLOSED: Allow all calls
        if self._state == CircuitState.CLOSED:
            return True

        # OPEN: Check if recovery timeout passed
        if self._state == CircuitState.OPEN:
            if self._opened_at is None:
                # Should never happen, but handle gracefully
                self._transition_to(CircuitState.HALF_OPEN)
                return True

            elapsed = (datetime.now(tz.utc) - self._opened_at).total_seconds()
            if elapsed >= self.recovery_timeout:
                # Try recovery
                self._transition_to(CircuitState.HALF_OPEN)
                return True
            else:
                # Still in recovery timeout
                self._total_blocked += 1
                return False

        # HALF_OPEN: Allow call to test recovery
        if self._state == CircuitState.HALF_OPEN:
            return True

        # Should never reach here
        return False

    def record_success(self) -> None:
        """Record successful call."""
        if self._state == CircuitState.CLOSED:
            # Reset failure counter on success
            self._failure_count = 0

        elif self._state == CircuitState.HALF_OPEN:
            # Count successes to close circuit
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def record_failure(self, error: Exception) -> None:
        """
        Record failed call.

        Args:
            error: Exception that caused the failure
        """
        self._total_failures += 1
        self._last_failure_time = datetime.now(tz.utc)

        if self._state == CircuitState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

        elif self._state == CircuitState.HALF_OPEN:
            # Failure during testing - reopen circuit
            self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """
        Transition to new state.

        Args:
            new_state: New circuit state
        """
        old_state = self._state
        self._state = new_state

        # Reset counters based on new state
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None

        elif new_state == CircuitState.OPEN:
            self._opened_at = datetime.now(tz.utc)
            self._success_count = 0

        elif new_state == CircuitState.HALF_OPEN:
            self._failure_count = 0
            self._success_count = 0

        # Log transition
        if self.enable_logging and old_state != new_state:
            logger.warning(
                f"⚡ Centrifugo Circuit Breaker: {old_state.value} → {new_state.value} "
                f"(failures={self._failure_count}, total_blocked={self._total_blocked})"
            )

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._opened_at = None

        if self.enable_logging:
            logger.info("🔄 Centrifugo Circuit Breaker reset")

    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "state": self._state.value,
            "total_calls": self._total_calls,
            "total_failures": self._total_failures,
            "total_blocked": self._total_blocked,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_rate": (
                self._total_failures / self._total_calls
                if self._total_calls > 0
                else 0.0
            ),
            "last_failure_time": (
                self._last_failure_time.isoformat()
                if self._last_failure_time
                else None
            ),
        }


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'CentrifugoCircuitBreaker',
    'CircuitState',
]
