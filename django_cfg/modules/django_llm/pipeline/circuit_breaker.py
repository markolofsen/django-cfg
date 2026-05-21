"""
Circuit breaker — one breaker instance, three states.

Wraps a single failure domain (one model / provider). Keyed usage — one
breaker per ``(model, provider)`` — is the caller's job; the router does
exactly that.

States:
    CLOSED     normal — calls flow through.
    OPEN       too many consecutive failures — fast-fail, no I/O, until a
               cooldown elapses.
    HALF_OPEN  cooldown elapsed — allow exactly one probe; a success closes
               the breaker, a failure re-opens it.

Pure and time-injectable: pass a ``now`` callable for deterministic tests.
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Callable


class CircuitState(str, Enum):
    """The three circuit-breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """A single circuit breaker.

    Args:
        failure_threshold: consecutive failures that trip CLOSED -> OPEN.
        cooldown: seconds an OPEN breaker waits before allowing a probe.
        now: monotonic clock, injectable for tests (default ``time.monotonic``).
    """

    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        cooldown: float = 30.0,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self._now = now

        self._state: CircuitState = CircuitState.CLOSED
        self._consecutive_failures: int = 0
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        """Current state, re-evaluating an elapsed OPEN cooldown."""
        if self._state is CircuitState.OPEN and self._cooldown_elapsed():
            self._state = CircuitState.HALF_OPEN
        return self._state

    def allow(self) -> bool:
        """Whether a call may proceed.

        CLOSED -> always; HALF_OPEN -> allow one probe; OPEN -> False until
        the cooldown elapses (which transitions it to HALF_OPEN).
        """
        return self.state is not CircuitState.OPEN

    def record_success(self) -> None:
        """A call succeeded — reset failures and close the breaker."""
        self._consecutive_failures = 0
        self._opened_at = None
        self._state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """A call failed — count it and open (or re-open) if past threshold.

        A failure during HALF_OPEN re-opens immediately; the failed probe
        is what HALF_OPEN exists to catch.
        """
        if self.state is CircuitState.HALF_OPEN:
            self._trip()
            return

        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._trip()

    def _trip(self) -> None:
        """Move to OPEN and start the cooldown."""
        self._state = CircuitState.OPEN
        self._opened_at = self._now()
        if self._consecutive_failures < self.failure_threshold:
            self._consecutive_failures = self.failure_threshold

    def _cooldown_elapsed(self) -> bool:
        """Whether the OPEN cooldown has fully elapsed."""
        if self._opened_at is None:
            return False
        return (self._now() - self._opened_at) >= self.cooldown
