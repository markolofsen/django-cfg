"""
OpenRouter embedder for real embedding generation.

OpenRouter exposes an OpenAI-compatible ``/embeddings`` endpoint, so the
provider's client (an ``OpenAI`` instance with ``base_url=
https://openrouter.ai/api/v1``) can call ``client.embeddings.create``
directly — no mock needed. This replaces the old MD5 mock path for the
project's canonical embedding models (``openai/text-embedding-3-small`` /
``-3-large``), which run on OpenRouter.

Unlike ``OpenAIEmbedder`` this:
- keeps the ``openai/`` model prefix (OpenRouter routes by the full slug);
- forwards an optional ``dimensions`` argument so callers can pin the
  output size (e.g. request ``text-embedding-3-large`` at 1536 dims so it
  shares pgvector columns with the small model).
"""

import logging
import time

from ..registry.pricing import calculate_embedding_cost
from ..core.types import EmbeddingResponse

logger = logging.getLogger(__name__)


class OpenRouterEmbedder:
    """Generates real embeddings via OpenRouter's OpenAI-compatible API."""

    def __init__(self, models_cache=None):
        self.models_cache = models_cache

    def generate(
        self,
        client,
        text: str,
        model: str,
        *,
        dimensions: int | None = None,
    ) -> EmbeddingResponse:
        """Generate a real embedding via OpenRouter.

        Args:
            client: OpenRouter client (OpenAI SDK pointed at openrouter.ai).
            text: Text to embed.
            model: Embedding model slug (keep the ``openai/`` prefix).
            dimensions: Optional output dimension. OpenAI's v3 models
                truncate natively when this is below their native size.

        Returns:
            EmbeddingResponse with the vector and cost/token metadata.
        """
        start_time = time.time()

        # OpenRouter routes by the full slug — do NOT strip the prefix
        # (that's the difference from OpenAIEmbedder).
        create_kwargs: dict = {"input": text, "model": model}
        if dimensions is not None:
            create_kwargs["dimensions"] = dimensions

        response = client.embeddings.create(**create_kwargs)

        embedding_data = response.data[0]
        embedding_vector = embedding_data.embedding

        tokens_used = response.usage.total_tokens
        cost = calculate_embedding_cost(tokens_used, model, self.models_cache)

        response_time = time.time() - start_time

        logger.debug(
            "OpenRouter embedding: model=%s tokens=%s cost=$%.6f dim=%s %.2fs",
            model, tokens_used, cost, len(embedding_vector), response_time,
        )

        return EmbeddingResponse(
            embedding=embedding_vector,
            tokens=tokens_used,
            cost=cost,
            model=model,
            text_length=len(text),
            dimension=len(embedding_vector),
            response_time=response_time,
        )
