"""
Budget helpers — one-liner access to per-model pricing for cost-aware model
selection. Thin facade over the LLMClient's already-loaded model catalogue (336
OpenRouter models with live `pricing`); the rest of the app shouldn't have to know
where the cache lives or what the price field is called.

    from modules.llm_router import import_llm
    budget = import_llm("registry.budget")

    budget.model_price("anthropic/claude-3.5-haiku")   # -> {"prompt": 0.8, "completion": 4.0} USD/1M
    budget.within_budget(slugs, max_price=0.3)         # -> [slugs whose prompt price <= 0.3]
    budget.cheapest(slugs)                             # -> the slug with the lowest prompt price
    budget.annotate(slugs)                             # -> [(slug, prompt_price)] cheapest-first

Prices are USD per 1M tokens (ModelPricing.prompt_price / completion_price).
Unknown / unpriced slugs → INFINITELY expensive, so a typo can never slip a costly
model past a budget filter.
"""
from __future__ import annotations

import logging
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

INF = float("inf")


def _client():
    from ..client.client import LLMClient
    return LLMClient()


def model_price(slug: str) -> Optional[dict]:
    """Return {'prompt': float, 'completion': float} USD/1M for `slug`, or None if unknown."""
    try:
        info = _client().get_model_info(slug)
    except Exception as exc:  # noqa: BLE001 — pricing must never crash a caller
        logger.warning("model_price(%s) failed: %s", slug, exc)
        return None
    pricing = getattr(info, "pricing", None) if info else None
    if pricing is None:
        return None
    return {"prompt": pricing.prompt_price, "completion": pricing.completion_price}


def prompt_price(slug: str) -> float:
    """Prompt (input) price USD/1M for `slug`; INF if unknown (so budget filters drop it)."""
    p = model_price(slug)
    return p["prompt"] if p else INF


def within_budget(slugs: Iterable[str], max_price: float) -> list[str]:
    """Keep only slugs whose PROMPT price is <= max_price (USD/1M). Unknown → dropped."""
    return [s for s in slugs if prompt_price(s) <= max_price]


def cheapest(slugs: Iterable[str]) -> Optional[str]:
    """The slug with the lowest prompt price (None if the list is empty)."""
    ranked = sorted(slugs, key=prompt_price)
    return ranked[0] if ranked else None


def annotate(slugs: Iterable[str]) -> list[tuple[str, float]]:
    """[(slug, prompt_price_usd_per_M), …] sorted cheapest-first — for display/logging."""
    return sorted(((s, prompt_price(s)) for s in slugs), key=lambda t: t[1])
