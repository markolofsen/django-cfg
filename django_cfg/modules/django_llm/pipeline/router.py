"""
Model-cascade router — try an ordered list of models, fall back on failure.

Each model gets its own ``CircuitBreaker`` (keyed by model id). A model
whose breaker is OPEN is skipped without a network call. Each attempted
model runs through the classified retry helper; whether it exhausts its
retry budget or hits a fatal error, the router advances to the next model.

When every model is exhausted or skipped, ``AllProvidersFailedError`` is
raised carrying a per-model ``attempts`` list for diagnostics.

Host-agnostic: imports only the error taxonomy and the sibling pipeline
modules. The per-model ``call`` callable is supplied by the caller.
"""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

from ..core.errors import AllProvidersFailedError, LLMError, classify_exception
from .circuit_breaker import CircuitBreaker
from .retry import DEFAULT_MAX_ATTEMPTS, retry_call

T = TypeVar("T")


class ModelRouter:
    """Cascading router over an ordered model list with per-model breakers.

    One router instance owns one breaker per model id, so circuit state
    persists across ``run()`` calls — a model that died on an earlier
    request stays fast-failed until its cooldown elapses.

    Args:
        models: ordered model ids — earlier is preferred.
        max_attempts: retry budget per model.
        base_delay / max_delay: backoff bounds passed to the retry helper.
        failure_threshold: consecutive failures that open a model's breaker.
        cooldown: OPEN-state cooldown in seconds.
        sleep / rng / now: injectable for deterministic tests.
    """

    def __init__(
        self,
        models: list[str],
        *,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        failure_threshold: int = 5,
        cooldown: float = 30.0,
        sleep: Callable[[float], None] = time.sleep,
        rng: Callable[[], float] = random.random,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        if not models:
            raise ValueError("models must be a non-empty list")
        self.models = list(models)
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self._sleep = sleep
        self._rng = rng
        self._breakers: dict[str, CircuitBreaker] = {
            model: CircuitBreaker(
                failure_threshold=failure_threshold,
                cooldown=cooldown,
                now=now,
            )
            for model in models
        }

    def breaker(self, model: str) -> CircuitBreaker:
        """The circuit breaker for ``model``."""
        return self._breakers[model]

    def run(self, call: Callable[[str], T], *, provider: str | None = None) -> T:
        """Try each model in turn until one succeeds.

        Args:
            call: ``call(model) -> result`` — the per-model invocation.
            provider: optional provider label, forwarded to classification.

        Returns:
            The result of the first model that succeeds.

        Raises:
            AllProvidersFailedError: every model failed or was skipped;
                ``.attempts`` holds one dict per model.
        """
        attempts: list[dict] = []

        for model in self.models:
            breaker = self._breakers[model]

            if not breaker.allow():
                attempts.append({
                    "model": model,
                    "provider": provider,
                    "skipped": True,
                    "reason": "circuit_open",
                    "error": None,
                })
                continue

            try:
                result = retry_call(
                    lambda m=model: call(m),
                    max_attempts=self.max_attempts,
                    base_delay=self.base_delay,
                    max_delay=self.max_delay,
                    provider=provider,
                    model=model,
                    sleep=self._sleep,
                    rng=self._rng,
                )
            except Exception as exc:  # noqa: BLE001 — recorded, then cascade
                error = classify_exception(exc, provider=provider, model=model)
                breaker.record_failure()
                attempts.append({
                    "model": model,
                    "provider": provider,
                    "skipped": False,
                    "reason": type(error).__name__,
                    "error": error,
                })
                continue

            breaker.record_success()
            return result

        raise AllProvidersFailedError(
            f"All {len(self.models)} model(s) failed or were skipped",
            attempts=attempts,
        )
