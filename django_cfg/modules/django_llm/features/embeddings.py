"""Public embedding helpers — the single embedding entry point for apps.

Apps call these through the host shim::

    from modules.llm_router import embed_fast, embed_quality

Two ready methods, both multilingual (EN/RU out of the box) and both
**1536-dim** so every pgvector column in the project stays uniform:

- :func:`embed_fast` / :func:`embed_fast_many` — ``text-embedding-3-small``
  (1536, ~$0.02/1M). The project DEFAULT (KB, tasks, clients, messages):
  cheap and effective.
- :func:`embed_quality` / :func:`embed_quality_many` —
  ``text-embedding-3-large`` requested at ``dimensions=1536`` (OpenAI
  truncates natively, negligible quality loss). For max-precision cases;
  same column shape.

All helpers return BARE vectors (``list[float]`` / ``list[list[float]]``),
matching the shape apps already use. For cost/token metadata, call
:func:`embed_response` (returns the full ``EmbeddingResponse``) or the
underlying ``LLMClient.generate_embedding``.

The embedding runs through ``LLMClient`` → the real OpenAI / OpenRouter
embedder (never the MD5 mock unless no provider key exists at all).
"""

from __future__ import annotations

from functools import lru_cache

from ..client import LLMClient
from ..core.types import EmbeddingResponse

# Project-canonical embedding models (OpenRouter slugs). 1536 everywhere.
FAST_MODEL = "openai/text-embedding-3-small"
QUALITY_MODEL = "openai/text-embedding-3-large"
EMBEDDING_DIMENSIONS = 1536


@lru_cache(maxsize=1)
def _client() -> LLMClient:
    """Process-wide embedding client (keys resolved via the integration seam)."""
    return LLMClient()


def embed_response(
    text: str,
    *,
    model: str = FAST_MODEL,
    dimensions: int | None = EMBEDDING_DIMENSIONS,
) -> EmbeddingResponse:
    """Embed one text and return the full response (vector + cost + tokens)."""
    return _client().generate_embedding(
        text=text, model=model, dimensions=dimensions,
    )


def embed_text(
    text: str,
    *,
    model: str = FAST_MODEL,
    dimensions: int | None = EMBEDDING_DIMENSIONS,
) -> list[float]:
    """Low-level: embed one text with an explicit model → bare vector.

    Returns ``[]`` for empty input (callers treat that as "skip").
    """
    if not text:
        return []
    return list(embed_response(text, model=model, dimensions=dimensions).embedding)


def embed_texts(
    texts: list[str],
    *,
    model: str = FAST_MODEL,
    dimensions: int | None = EMBEDDING_DIMENSIONS,
) -> list[list[float]]:
    """Low-level: embed a batch with an explicit model → list of vectors.

    One-by-one under the hood (the handler caches per text). Empty strings
    map to ``[]`` so the output index lines up with the input.
    """
    return [
        embed_text(t, model=model, dimensions=dimensions) for t in texts
    ]


# ── Ready methods ────────────────────────────────────────────────────

def embed_fast(text: str) -> list[float]:
    """Default embedding: text-embedding-3-small @ 1536. → bare vector."""
    return embed_text(text, model=FAST_MODEL, dimensions=EMBEDDING_DIMENSIONS)


def embed_fast_many(texts: list[str]) -> list[list[float]]:
    """Default batch embedding: text-embedding-3-small @ 1536."""
    return embed_texts(texts, model=FAST_MODEL, dimensions=EMBEDDING_DIMENSIONS)


def embed_quality(text: str) -> list[float]:
    """High-precision embedding: text-embedding-3-large @ 1536. → bare vector."""
    return embed_text(text, model=QUALITY_MODEL, dimensions=EMBEDDING_DIMENSIONS)


def embed_quality_many(texts: list[str]) -> list[list[float]]:
    """High-precision batch embedding: text-embedding-3-large @ 1536."""
    return embed_texts(texts, model=QUALITY_MODEL, dimensions=EMBEDDING_DIMENSIONS)


__all__ = [
    "FAST_MODEL",
    "QUALITY_MODEL",
    "EMBEDDING_DIMENSIONS",
    "EmbeddingResponse",
    "embed_response",
    "embed_text",
    "embed_texts",
    "embed_fast",
    "embed_fast_many",
    "embed_quality",
    "embed_quality_many",
]
