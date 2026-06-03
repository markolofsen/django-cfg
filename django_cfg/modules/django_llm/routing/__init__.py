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
    extract, extract_chat, classify, chat_with_tools, escalate,
    aextract, aextract_chat, aclassify, achat_with_tools, aescalate,
    extract_many, classify_many,
)

__all__ = [
    "LLMRouter",
    "LLMRouterError",
    # sync presets
    "extract",
    "extract_chat",
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
