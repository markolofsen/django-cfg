"""
Classified retry — run a callable, retry only transient failures.

On failure the raw exception is mapped through ``classify_exception()``;
the retry continues only while the classified ``LLMError.retryable`` is
True. Fatal errors (auth, bad request, credits) give up immediately.

Backoff is exponential with full jitter — ``random(0, min(cap, base *
2**n))`` — so a fleet of workers does not retry in lockstep. When the
error is an ``LLMRateLimitError`` carrying ``retry_after``, that value is
honored verbatim instead of the jittered backoff.

``sleep`` and ``rng`` are injectable so tests never actually sleep.
"""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

from ..core.errors import LLMError, LLMRateLimitError, classify_exception

T = TypeVar("T")

DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 1.0
DEFAULT_MAX_DELAY = 60.0


def compute_backoff(
    attempt: int,
    *,
    base: float = DEFAULT_BASE_DELAY,
    cap: float = DEFAULT_MAX_DELAY,
    rng: Callable[[], float] = random.random,
) -> float:
    """Full-jitter exponential backoff for a zero-based attempt index.

    ``sleep = random(0, min(cap, base * 2**attempt))``.
    """
    ceiling = min(cap, base * (2 ** attempt))
    return rng() * ceiling


def retry_call(
    func: Callable[[], T],
    *,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    provider: str | None = None,
    model: str | None = None,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> T:
    """Run ``func`` with classified retry and jittered backoff.

    Args:
        func: the zero-argument callable to execute.
        max_attempts: total attempts including the first (>= 1).
        base_delay: backoff base in seconds.
        max_delay: backoff cap in seconds.
        provider / model: call context, forwarded to ``classify_exception``.
        sleep: blocking sleep, injectable for tests.
        rng: ``[0, 1)`` random source for jitter, injectable for tests.

    Returns:
        Whatever ``func`` returns on the first successful attempt.

    Raises:
        LLMError: the classified error — raised immediately when it is
            fatal, or after ``max_attempts`` retryable failures.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    attempt = 0
    while True:
        try:
            return func()
        except Exception as exc:  # noqa: BLE001 — re-raised as classified LLMError
            error = classify_exception(
                exc, provider=provider, model=model, attempt=attempt + 1
            )
            attempt += 1

            # Fatal, or budget exhausted — give up with the typed error.
            if not error.retryable or attempt >= max_attempts:
                raise error from exc

            sleep(_delay_for(error, attempt - 1, base_delay, max_delay, rng))


def _delay_for(
    error: LLMError,
    attempt_index: int,
    base: float,
    cap: float,
    rng: Callable[[], float],
) -> float:
    """Seconds to wait before the next attempt.

    Honors ``Retry-After`` on a rate-limit error; otherwise full jitter.
    """
    if isinstance(error, LLMRateLimitError) and error.retry_after is not None:
        return float(error.retry_after)
    return compute_backoff(attempt_index, base=base, cap=cap, rng=rng)
