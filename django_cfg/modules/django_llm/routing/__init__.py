"""Routing & ergonomics layer — pick an LLM by *job*, not by model.

Sits between the low-level reliability mechanism (``pipeline/`` — retry,
circuit breaker, cost) and the public API:

- ``LLMRouter`` — cascading multi-model client (primary→fallback) over
  ``pipeline.ModelRouter``, with ``.parse()`` (structured output) and
  ``.complete()`` (raw text). ``LLMRouter.for_role(role)`` builds the chain
  from the catalog's recommendation.
- task presets (``extract`` / ``classify`` / ``chat_with_tools`` / ``escalate``)
  — thin wrappers that map a role to its model chain so callers never pass a
  model slug. Async twins (``aextract`` …) and fan-out helpers
  (``extract_many`` / ``classify_many``) run the same sync logic concurrently.
"""

from .llm_router import LLMRouter, LLMRouterError
from .presets import (
    achat_with_tools,
    aclassify,
    aescalate,
    aextract,
    aextract_chat,
    chat_with_tools,
    classify,
    classify_many,
    escalate,
    extract,
    extract_chat,
    extract_chat_bulk,
    extract_many,
)
from .providers import (
    BALANCED,
    CHEAPEST,
    THROUGHPUT,
    ProviderPolicy,
    ProviderSort,
)

__all__ = [
    "LLMRouter",
    "LLMRouterError",
    # provider routing policy (which upstream serves a model)
    "ProviderPolicy",
    "ProviderSort",
    "BALANCED",
    "THROUGHPUT",
    "CHEAPEST",
    # sync presets
    "extract",
    "extract_chat",
    "extract_chat_bulk",
    "classify",
    "chat_with_tools",
    "escalate",
    # async twins
    "aextract",
    "aextract_chat",
    "aclassify",
    "achat_with_tools",
    "aescalate",
    # fan-out
    "extract_many",
    "classify_many",
]
