"""
OpenRouter model discovery by capability.

Finds OpenRouter models by capability — in particular **free** models that
also support **structured output** (JSON-schema / response_format).

The model registry's `ModelsCache` does not keep `supported_parameters`,
so it cannot tell whether a model enforces structured output. This module
queries the public OpenRouter catalogue directly (`/api/v1/models`, no API
key needed) and exposes that capability.

Rate-limit reality: OpenRouter `:free` models share a hard cap (~20 req/min
and ~1000 req/day across all free models). They are fine for experiments
and low-volume traffic, but NOT for high-throughput backlogs — at backlog
concurrency the cap is hit in seconds and every further call eats a
retry-delay before falling through to a paid model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger("django_cfg.django_llm.registry")

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# A model can be driven with a JSON schema if it advertises either of these.
STRUCTURED_PARAMS = ("structured_outputs", "response_format")


@dataclass
class ORModel:
    """One OpenRouter catalogue entry, reduced to the fields we care about."""

    id: str
    name: str
    context_length: int
    prompt_price: float       # USD per token (0.0 == free)
    completion_price: float   # USD per token (0.0 == free)
    supported_parameters: list[str] = field(default_factory=list)

    @property
    def is_free(self) -> bool:
        return self.prompt_price == 0.0 and self.completion_price == 0.0

    @property
    def supports_structured(self) -> bool:
        return any(p in self.supported_parameters for p in STRUCTURED_PARAMS)


def _to_float(value: object) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


def fetch_openrouter_models(timeout: float = 30.0) -> list[ORModel]:
    """
    Fetch the full OpenRouter model catalogue.

    The endpoint is public — no API key required.
    """
    resp = httpx.get(OPENROUTER_MODELS_URL, timeout=timeout)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    models: list[ORModel] = []
    for entry in data:
        pricing = entry.get("pricing") or {}
        models.append(
            ORModel(
                id=entry.get("id", ""),
                name=entry.get("name", ""),
                context_length=int(entry.get("context_length") or 0),
                prompt_price=_to_float(pricing.get("prompt")),
                completion_price=_to_float(pricing.get("completion")),
                supported_parameters=list(entry.get("supported_parameters") or []),
            )
        )
    logger.info("Fetched %d models from OpenRouter", len(models))
    return models


def find_free_structured_models(min_context: int = 16000) -> list[ORModel]:
    """
    Free models that support structured output, large enough for real work.

    Args:
        min_context: drop models whose context window is below this — a
            structured-extraction prompt (system + payload) often runs
            ~8-12k tokens.

    Returns:
        Free + structured-capable models, widest context window first.
    """
    models = [
        m
        for m in fetch_openrouter_models()
        if m.is_free and m.supports_structured and m.context_length >= min_context
    ]
    models.sort(key=lambda m: m.context_length, reverse=True)
    return models
