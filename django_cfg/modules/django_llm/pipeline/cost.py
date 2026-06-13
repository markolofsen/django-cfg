"""
Cost observability — per-attempt cost tracking and the wasted-spend metric.

``django_llm``'s success-only logging hides a real leak: a response that
arrives and is billed, then fails JSON / schema validation, is retried on
a pricier model — and that spend is recorded nowhere. This layer makes
every attempt (success *or* failure) emit a structured ``CostEvent``, so
"wasted spend" — the cost of attempts that did not produce the final
answer — becomes a first-class, queryable metric.

Money is ``Decimal`` everywhere; never float arithmetic.

``alert_wasted_call`` is the cost-leak alarm: a billed-but-unusable
response fires a throttled Telegram warning so a systemic failure surfaces
where a human looks — generalized from an earlier host-app
``_alert_wasted_llm_call`` shipped to production.
Host coupling (Telegram) goes only through the ``_integration.py`` seam,
and every telegram / throttle failure is swallowed: observability must
never break a real request.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable

logger = logging.getLogger(__name__)

# Outcomes that count as the run's final answer — every other outcome is
# a billed-but-discarded attempt and so counts toward wasted spend.
FINAL_SUCCESS_OUTCOMES = frozenset({"success"})

# One wasted-spend alert per model per this window (seconds) — a systemic
# failure must not flood the channel.
ALERT_THROTTLE_SECONDS = 600

_COST_DISPLAY_PRECISION = Decimal("0.000001")


def _format_cost_for_display(cost: Decimal) -> str:
    """Round to micro-cents and strip trailing zeros for human-readable cost."""
    quantized = cost.quantize(_COST_DISPLAY_PRECISION)
    s = f"{quantized:f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


@dataclass(slots=True)
class CostEvent:
    """One LLM attempt — success or failure — and what it cost.

    Every attempt emits one of these, so spend on discarded attempts is
    never invisible. ``cost_usd`` is a ``Decimal`` — money is never float.

    Attributes:
        model: the resolved model id the attempt ran against.
        provider: provider label (``openrouter``, ``openai``, …).
        prompt_tokens / completion_tokens: per-direction token counts.
        tokens: total tokens billed (prompt + completion when not given).
        cost_usd: USD billed for the attempt, ``Decimal``.
        outcome: ``success`` | ``validation_failed`` | ``transport_failed``
            | … — anything not in ``FINAL_SUCCESS_OUTCOMES`` is wasted spend.
        tier: ``primary`` | ``fallback`` — chain position, when known.
        retry_index: zero-based attempt index within the run.
        cache_hit: whether the response was served from cache (cost $0).
        latency_ms: wall-clock latency of the attempt.
        request_id: provider/request correlation id, when known.
    """

    model: str
    provider: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    tokens: int = 0
    cost_usd: Decimal = field(default_factory=lambda: Decimal("0"))
    outcome: str = "success"
    tier: str | None = None
    retry_index: int = 0
    cache_hit: bool = False
    latency_ms: float | None = None
    request_id: str | None = None

    def __post_init__(self) -> None:
        # Coerce cost to Decimal defensively — a float would poison every
        # downstream sum. ``Decimal(str(x))`` avoids float-binary drift.
        if not isinstance(self.cost_usd, Decimal):
            self.cost_usd = Decimal(str(self.cost_usd))
        # Fall back to prompt + completion when total tokens not supplied.
        if not self.tokens:
            self.tokens = self.prompt_tokens + self.completion_tokens

    @property
    def is_final_success(self) -> bool:
        """Whether this attempt produced the run's accepted answer."""
        return self.outcome in FINAL_SUCCESS_OUTCOMES

    @property
    def is_wasted(self) -> bool:
        """Whether this attempt was billed but did not produce the answer."""
        return not self.is_final_success

    def to_dict(self) -> dict:
        """A JSON-friendly view (``cost_usd`` rendered as a string)."""
        return {
            "model": self.model,
            "provider": self.provider,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "tokens": self.tokens,
            "cost_usd": str(self.cost_usd),
            "outcome": self.outcome,
            "tier": self.tier,
            "retry_index": self.retry_index,
            "cache_hit": self.cache_hit,
            "latency_ms": self.latency_ms,
            "request_id": self.request_id,
        }


class CostTracker:
    """Accumulates ``CostEvent``s for one logical LLM run.

    In-process and intentionally simple — one tracker per request /
    normalization. ``total_cost`` is everything billed; ``wasted_spend``
    is the slice of that which never produced the final answer.
    """

    def __init__(self) -> None:
        self._events: list[CostEvent] = []

    def record(self, event: CostEvent) -> CostEvent:
        """Append an attempt's cost event. Returns the event for chaining."""
        self._events.append(event)
        return event

    @property
    def events(self) -> list[CostEvent]:
        """A copy of the recorded events, in record order."""
        return list(self._events)

    @property
    def total_cost(self) -> Decimal:
        """Total USD billed across every recorded attempt."""
        return sum((e.cost_usd for e in self._events), Decimal("0"))

    @property
    def total_tokens(self) -> int:
        """Total tokens billed across every recorded attempt."""
        return sum(e.tokens for e in self._events)

    @property
    def wasted_spend(self) -> Decimal:
        """USD billed for attempts that did not produce the final answer.

        Every event whose ``outcome`` is not a final success — a billed
        response that failed validation, a discarded retry — is wasted.
        """
        return sum(
            (e.cost_usd for e in self._events if e.is_wasted),
            Decimal("0"),
        )

    def snapshot(self) -> dict:
        """A flat observability view of the run so far.

        ``Decimal`` money is rendered as strings so the dict is directly
        JSON-serializable for logging / metrics export.
        """
        return {
            "attempts": len(self._events),
            "total_cost_usd": str(self.total_cost),
            "total_tokens": self.total_tokens,
            "wasted_spend_usd": str(self.wasted_spend),
            "events": [e.to_dict() for e in self._events],
        }


# ── Wasted-spend alert ────────────────────────────────────────────────────

# Per-model timestamp of the last alert sent — the in-process throttle.
_last_alert_at: dict[str, float] = {}


def _default_send_warning(warning: str, context: dict) -> None:
    """Send a Telegram warning through the host integration seam.

    Imported lazily so importing this module never drags in the host;
    any failure is the caller's to swallow.
    """
    from .._integration import DjangoTelegram

    DjangoTelegram.send_warning(warning=warning, context=context)


def alert_wasted_call(
    model: str,
    tokens: int,
    cost_usd: Decimal | float | str,
    error: str,
    *,
    provider: str | None = None,
    send_warning: Callable[[str, dict], None] = _default_send_warning,
    now: Callable[[], float] = time.monotonic,
) -> bool:
    """Alert on a billed-but-unusable LLM response — the cost leak.

    A response that arrived (and was billed) then failed JSON / schema
    validation, or was discarded after a retry, is pure wasted spend. The
    router would otherwise retry the next — often pricier — model silently.
    This fires a Telegram warning so the leak surfaces.

    Throttled to one alert per model per ``ALERT_THROTTLE_SECONDS`` so a
    systemic failure cannot flood the channel. Fail-safe: a telegram or
    throttle error is swallowed and never propagates to the call path.

    Args:
        model: the model whose billed response was unusable.
        tokens: tokens billed for the wasted call.
        cost_usd: USD billed — coerced to ``Decimal``.
        error: the validation / discard error message.
        provider: optional provider label, included in the alert context.
        send_warning: ``send_warning(warning, context)`` sink — injectable
            for tests; defaults to the ``_integration`` Telegram seam.
        now: monotonic clock, injectable for deterministic throttle tests.

    Returns:
        True if an alert was sent, False if throttled or it failed.
    """
    try:
        last = _last_alert_at.get(model)
        ts = now()
        if last is not None and (ts - last) < ALERT_THROTTLE_SECONDS:
            return False
        _last_alert_at[model] = ts

        cost = cost_usd if isinstance(cost_usd, Decimal) else Decimal(str(cost_usd))
        context = {
            "model": model,
            "tokens": tokens,
            "cost_usd": _format_cost_for_display(cost),
            "error": (error or "")[:300],
        }
        if provider:
            context["provider"] = provider

        send_warning(
            "LLM call billed but response unusable — wasted spend",
            context,
        )
        return True
    except Exception:  # noqa: BLE001 — observability must never break a call
        logger.warning("alert_wasted_call failed for model=%s", model, exc_info=True)
        return False
