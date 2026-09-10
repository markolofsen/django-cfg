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

import logging
from dataclasses import dataclass
from typing import Any, Optional

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

    @property
    def total_tokens(self) -> int:
        return self.tokens_input + self.tokens_output


def price_run(usage: Any, model: str) -> RunCost:
    """Turn a pydantic-ai ``RunUsage`` + model slug into a ``RunCost``.

    Args:
        usage: the run's usage object (``RunUsage``). Read via ``input_tokens`` /
            ``output_tokens`` — the split the pricing needs. ``None``-safe.
        model: the concrete slug that served the run
            (``AgentRunResult.response.model_name``). Empty when unknown → the run
            is left unpriced rather than mispriced against a guessed model.

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
        from modules.django_llm.registry.models import ModelsCache

        cost_usd = ModelsCache().calculate_cost_from_usage(
            model,
            {"prompt_tokens": tokens_input, "completion_tokens": tokens_output},
        )
    except Exception:
        # Telemetry must not break the turn — see module docstring.
        logger.exception("[cost] could not price run for model=%s", model)
        cost_usd = None

    return RunCost(tokens_input, tokens_output, cost_usd, model)
