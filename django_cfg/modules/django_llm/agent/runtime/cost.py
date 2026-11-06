"""Price an agent run — the one place the harness turns tokens into dollars.

pydantic-ai gives a run's `RunUsage` (an input/output token split) and the concrete
slug that served it (`AgentRunResult.response.model_name`). The transport plane
already owns the arithmetic — `registry/models.py::ModelPricing.cost`, fed from the
live OpenRouter catalogue — so this module does not compute anything itself. It is
the *adapter*: RunUsage-shaped in, `RunCost` out, and it never raises.

Why never raise: cost is telemetry, not the answer. A missing OpenRouter key, a slug
the catalogue has never seen, a registry fetch timeout — none of these should turn a
successful chat turn into an error. Every failure path returns a `RunCost` with
`cost_usd=None` and the tokens it *does* know, so the caller can still record token
counts and simply show cost as unknown.
"""

from __future__ import annotations

import asyncio
import functools
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RunCost:
    """What one agent run cost, as far as we can tell.

    `cost_usd` is ``None`` when the run could not be priced (no key, unknown model,
    registry unavailable) — distinct from ``0.0``, which is a real free-tier price.
    The token counts are always populated when usage was available, even when the
    dollar figure is not.
    """

    tokens_input: int
    tokens_output: int
    cost_usd: Optional[float]
    model: str
    #: True when ``cost_usd`` came from the caller's fallback table, not the registry.
    estimated: bool = False

    @property
    def total_tokens(self) -> int:
        return self.tokens_input + self.tokens_output


#: USD per million tokens: ``{"input": 0.25, "output": 2.0}``.
PriceRow = Mapping[str, float]


def estimate_cost(tokens_input: int, tokens_output: int, row: PriceRow) -> float:
    """Dollars for a run at ``row`` (USD per million tokens, keys ``input`` and ``output``)."""
    return (tokens_input * row["input"] + tokens_output * row["output"]) / 1_000_000


def price_run(
    usage: Any,
    model: str,
    *,
    offline: bool = False,
    fallback_prices: Mapping[str, PriceRow] | None = None,
    default_price: PriceRow | None = None,
) -> RunCost:
    """Turn a pydantic-ai ``RunUsage`` + model slug into a ``RunCost``.

    Args:
        usage: the run's usage object (``RunUsage``). Read via ``input_tokens`` /
            ``output_tokens`` — the split the pricing needs. ``None``-safe.
        model: the concrete slug that served the run
            (``AgentRunResult.response.model_name``). Empty when unknown → the run
            is left unpriced rather than mispriced against a guessed model.
        offline: never touch the network. The registry may fetch its catalogue over
            HTTP on a cold cache (up to 20 s); ``offline=True`` reads only what the
            on-disk cache already holds, so a caller need not wrap the call in a timeout.
        fallback_prices: ``{slug: {"input": .., "output": ..}}`` (USD per million tokens)
            used when the registry cannot price the run. The result is flagged
            ``estimated=True``.
        default_price: the row for a slug absent from ``fallback_prices``. Set it to the
            dearest row you know so an unknown model is never priced as free. Without
            it (and without a table row) the cost stays ``None``.

    Returns:
        A ``RunCost``. Always returns; never raises.
    """
    tokens_input = int(getattr(usage, "input_tokens", 0) or 0)
    tokens_output = int(getattr(usage, "output_tokens", 0) or 0)

    if not model:
        # No slug means we cannot look up a price. Record the tokens, leave the
        # dollar figure unknown — a guessed model would be worse than no number.
        return RunCost(tokens_input, tokens_output, None, "")

    cost_usd: Optional[float] = None
    try:
        from django_cfg.modules.django_llm.registry.models import ModelsCache

        cost_usd = ModelsCache().calculate_cost_from_usage(
            model,
            {"prompt_tokens": tokens_input, "completion_tokens": tokens_output},
            fetch=not offline,
        )
    except Exception:
        # Telemetry must not break the turn — see module docstring.
        logger.exception("[cost] could not price run for model=%s", model)
        cost_usd = None

    if cost_usd is None:
        row = (fallback_prices or {}).get(model, default_price)
        if row is not None:
            logger.warning("[cost] model=%s not priced by the registry; estimated from the caller's table", model)
            return RunCost(tokens_input, tokens_output, estimate_cost(tokens_input, tokens_output, row), model, True)

    return RunCost(tokens_input, tokens_output, cost_usd, model)


Pricer = Callable[[Any, str], RunCost]


async def aprice_run(
    usage: Any,
    model: str,
    pricer: Pricer | None = None,
    *,
    timeout_s: float = 3.0,
    fallback_prices: Mapping[str, PriceRow] | None = None,
    default_price: PriceRow | None = None,
) -> RunCost:
    """``pricer`` (default ``price_run``) off the event loop, bounded by ``timeout_s``. Never raises.

    ``price_run`` is blocking (a cold registry fetches over HTTP). When the pricer fails or
    times out the tokens are still reported, and the cost is estimated from the fallback
    table when the caller gave one (``estimated=True``), else ``None``.
    """
    call = pricer or functools.partial(price_run, fallback_prices=fallback_prices, default_price=default_price)
    try:
        return await asyncio.wait_for(asyncio.to_thread(call, usage, model), timeout_s)
    except Exception:  # noqa: BLE001 - cost is telemetry; an unpriced run is reported, never an error
        logger.warning("[cost] pricing %r failed or timed out", model, exc_info=True)
        tin, tout = int(getattr(usage, "input_tokens", 0) or 0), int(getattr(usage, "output_tokens", 0) or 0)
        row = (fallback_prices or {}).get(model, default_price)
        if row is None:
            return RunCost(tin, tout, None, model)
        return RunCost(tin, tout, estimate_cost(tin, tout, row), model, True)
