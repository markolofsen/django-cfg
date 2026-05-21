"""
Client-side rate limiter — a dual token bucket plus a 429 cooldown.

LLM quotas are token-denominated as much as request-denominated, so one
bucket is not enough: a request burst can trip RPM while a single large
prompt trips TPM. ``RateLimiter`` runs two buckets — requests-per-minute
and tokens-per-minute — and ``.acquire()`` returns the larger of the two
waits (and of any active 429 cooldown).

Non-blocking by design: the component never sleeps. ``.acquire()`` returns
the seconds the caller should wait; the caller owns the sleep. Both buckets
refill continuously at ``limit / 60`` per second.

Pure, in-process, time-injectable — pass a ``now`` callable for
deterministic tests. A per-process bucket undercounts across Django's
gunicorn/uwsgi workers; a Redis-backed shared limiter is the eventual
multi-worker fix and a later integration concern.
"""

from __future__ import annotations

import time
from typing import Callable


class _TokenBucket:
    """A single continuously-refilling token bucket.

    Holds at most ``capacity`` tokens, refills at ``capacity / 60`` per
    second (``capacity`` is a per-minute limit). ``take`` is optimistic: it
    always consumes the amount, letting the level go negative, and reports
    how long that debt takes to refill — that wait is what the caller
    serves before the next request actually proceeds.
    """

    def __init__(self, capacity: float, now: Callable[[], float]) -> None:
        self.capacity = capacity
        self._refill_per_sec = capacity / 60.0
        self._now = now
        self._tokens = capacity
        self._updated = now()

    def _refill(self) -> None:
        """Credit tokens accrued since the last update, capped at capacity."""
        t = self._now()
        elapsed = t - self._updated
        if elapsed > 0:
            self._tokens = min(self.capacity, self._tokens + elapsed * self._refill_per_sec)
            self._updated = t

    def take(self, amount: float) -> float:
        """Consume ``amount`` tokens; return seconds of refill debt incurred.

        Returns 0.0 when the bucket had enough tokens. A negative balance
        after the take is converted to a wait via the refill rate.
        """
        self._refill()
        self._tokens -= amount
        if self._tokens >= 0:
            return 0.0
        return -self._tokens / self._refill_per_sec


class RateLimiter:
    """A dual token bucket — one for RPM, one for TPM — with a 429 cooldown.

    Args:
        rpm: requests-per-minute cap; ``None`` leaves requests unlimited.
        tpm: tokens-per-minute cap; ``None`` leaves tokens unlimited.
        now: monotonic clock, injectable for tests (default ``time.monotonic``).
    """

    def __init__(
        self,
        *,
        rpm: float | None = None,
        tpm: float | None = None,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._now = now
        self._requests = _TokenBucket(rpm, now) if rpm is not None else None
        self._tokens = _TokenBucket(tpm, now) if tpm is not None else None
        self._cooldown_until: float = 0.0

    def acquire(self, estimated_tokens: float = 0) -> float:
        """Reserve one request and ``estimated_tokens``; return seconds to wait.

        Consumes 1 token from the RPM bucket and ``estimated_tokens`` from
        the TPM bucket, then returns the longest of: the RPM refill debt,
        the TPM refill debt, and any remaining 429 cooldown. ``0.0`` means
        the caller may proceed immediately. The limiter never sleeps.
        """
        wait = self._cooldown_remaining()
        if self._requests is not None:
            wait = max(wait, self._requests.take(1))
        if self._tokens is not None:
            wait = max(wait, self._tokens.take(estimated_tokens))
        return wait

    def cooldown(self, seconds: float) -> None:
        """Force a cooldown — call this on a provider 429.

        Until ``seconds`` elapse, every ``acquire()`` returns at least the
        remaining cooldown. Extends but never shortens an active cooldown.
        """
        self._cooldown_until = max(self._cooldown_until, self._now() + seconds)

    def _cooldown_remaining(self) -> float:
        """Seconds left on an active 429 cooldown, or 0.0 if none."""
        remaining = self._cooldown_until - self._now()
        return remaining if remaining > 0 else 0.0
