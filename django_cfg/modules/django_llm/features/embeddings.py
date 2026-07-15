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

import logging
from functools import lru_cache

from ..client import LLMClient
from ..core.types import EmbeddingResponse
from ..embeddings.mock_embedder import is_mock_embedding

logger = logging.getLogger(__name__)

# Project-canonical embedding models (OpenRouter slugs). 1536 everywhere.
FAST_MODEL = "openai/text-embedding-3-small"
QUALITY_MODEL = "openai/text-embedding-3-large"
EMBEDDING_DIMENSIONS = 1536


@lru_cache(maxsize=1)
def _client() -> LLMClient:
    """Process-wide embedding client (keys resolved via the integration seam)."""
    return LLMClient()


def _vector_or_empty(response: EmbeddingResponse) -> list[float]:
    """Bare vector — unless it is MD5 noise, in which case ``[]``.

    This is the guard that keeps a mock out of every pgvector column in the
    project, and it lives HERE, at the one public seam, rather than in each app
    that persists a vector. Apps already treat ``[]`` as "no embedding, skip the
    write", so a keyless environment degrades to "this row has no vector" —
    visible, recoverable, and honest — instead of "this row has a vector that
    means nothing", which looks like a working system and is not.
    """
    if is_mock_embedding(response):
        logger.error(
            "Refusing to return a MOCK embedding as a real vector — no provider "
            "key is configured. This row will have NO embedding. Set "
            "OPENROUTER_API_KEY (or OPENAI_API_KEY) and re-run.",
        )
        return []
    return list(response.embedding)


def embed_response(
    text: str,
    *,
    model: str = FAST_MODEL,
    dimensions: int | None = EMBEDDING_DIMENSIONS,
) -> EmbeddingResponse:
    """Embed one text and return the full response (vector + cost + tokens).

    Unlike :func:`embed_text`, this hands back the raw response — a mock
    included. Check :func:`~..embeddings.mock_embedder.is_mock_embedding` before
    persisting anything you get from here.
    """
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

    Returns ``[]`` for empty input, and ``[]`` for a mock (callers treat that as
    "skip" in both cases — see :func:`_vector_or_empty`).
    """
    if not text:
        return []
    return _vector_or_empty(embed_response(text, model=model, dimensions=dimensions))


def embed_texts(
    texts: list[str],
    *,
    model: str = FAST_MODEL,
    dimensions: int | None = EMBEDDING_DIMENSIONS,
) -> list[list[float]]:
    """Low-level: embed a batch with an explicit model → list of vectors.

    ONE request for all cache misses (not N — see
    ``EmbeddingRequestHandler.generate_embeddings``). Empty strings map to ``[]``
    without costing a token, so the output index always lines up with the input.
    """
    if not texts:
        return []

    # The provider rejects an empty input and an empty text has no embedding, so
    # the empties never leave here — they are re-inserted as `[]` on the way out.
    fillable = [(index, text) for index, text in enumerate(texts) if text]
    vectors: list[list[float]] = [[] for _ in texts]
    if not fillable:
        return vectors

    responses = _client().generate_embeddings(
        texts=[text for _, text in fillable], model=model, dimensions=dimensions,
    )
    for (index, _), response in zip(fillable, responses):
        vectors[index] = _vector_or_empty(response)
    return vectors


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
