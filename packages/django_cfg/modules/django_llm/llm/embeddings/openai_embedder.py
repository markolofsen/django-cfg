"""
OpenAI embedder for real embedding generation.

Uses OpenAI Embeddings API to generate high-quality embeddings.
"""

import logging
import time

from ..costs import calculate_embedding_cost
from ..models import EmbeddingResponse

logger = logging.getLogger(__name__)


class OpenAIEmbedder:
    """Generates real embeddings using OpenAI API."""

    def __init__(self, models_cache=None):
        """
        Initialize OpenAI embedder.

        Args:
            models_cache: Optional models cache for cost calculation
        """
        self.models_cache = models_cache

    def generate(self, client, text: str, model: str) -> EmbeddingResponse:
        """
        Generate real embedding via OpenAI API.

        Args:
            client: OpenAI client instance
            text: Text to generate embedding for
            model: Embedding model to use

        Returns:
            EmbeddingResponse with embedding vector and metadata
        """
        start_time = time.time()

        # Remove provider prefix if present
        api_model = model
        if model.startswith("openai/"):
            api_model = model.replace("openai/", "")

        logger.debug(f"Generating embedding with model: {api_model}")

        # Make API call
        response = client.embeddings.create(
            input=text,
            model=api_model
        )

        # Extract embedding data
        embedding_data = response.data[0]
        embedding_vector = embedding_data.embedding

        # Calculate tokens and cost
        tokens_used = response.usage.total_tokens
        cost = calculate_embedding_cost(tokens_used, model, self.models_cache)

        response_time = time.time() - start_time

        logger.debug(
            f"Generated embedding: {tokens_used} tokens, "
            f"${cost:.6f}, {response_time:.2f}s"
        )

        return EmbeddingResponse(
            embedding=embedding_vector,
            tokens=tokens_used,
            cost=cost,
            model=model,
            text_length=len(text),
            dimension=len(embedding_vector),
            response_time=response_time
        )
