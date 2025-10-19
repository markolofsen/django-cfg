"""
Mock embedder for providers without embedding support.

Generates mock embeddings using MD5 hash for OpenRouter and similar providers.
"""

import hashlib
import logging
import time

from ..costs import calculate_embedding_cost
from ..models import EmbeddingResponse

logger = logging.getLogger(__name__)


class MockEmbedder:
    """Generates mock embeddings for providers without embedding support."""

    # Standard embedding dimension for ada-002 compatibility
    EMBEDDING_DIMENSION = 1536

    def __init__(self, models_cache=None):
        """
        Initialize mock embedder.

        Args:
            models_cache: Optional models cache for cost calculation
        """
        self.models_cache = models_cache

    def generate(self, text: str, model: str) -> EmbeddingResponse:
        """
        Generate mock embedding using MD5 hash.

        This is a workaround for OpenRouter which doesn't support embeddings.
        The mock embedding is deterministic based on text content.

        Args:
            text: Text to generate embedding for
            model: Model name (used for cost estimation)

        Returns:
            EmbeddingResponse with mock embedding vector and warning
        """
        start_time = time.time()

        logger.warning(
            "Using mock embedding generation. "
            "OpenRouter doesn't support embedding models."
        )

        # Create mock embedding from text hash
        mock_embedding = self._create_mock_vector(text)

        # Estimate tokens and cost
        tokens_used = len(text.split())  # Rough estimate
        cost = calculate_embedding_cost(tokens_used, model, self.models_cache)

        response_time = time.time() - start_time

        logger.debug(
            f"Generated mock embedding: {tokens_used} tokens (estimated), "
            f"${cost:.6f}, {response_time:.2f}s"
        )

        return EmbeddingResponse(
            embedding=mock_embedding,
            tokens=tokens_used,
            cost=cost,
            model=model,
            text_length=len(text),
            dimension=len(mock_embedding),
            response_time=response_time,
            warning="Mock embedding - OpenRouter doesn't support embedding models"
        )

    def _create_mock_vector(self, text: str) -> list:
        """
        Create mock embedding vector from text hash.

        Uses MD5 hash to create a deterministic vector that's consistent
        for the same text but different for different texts.

        Args:
            text: Input text

        Returns:
            List of floats representing the mock embedding
        """
        # Generate MD5 hash of text
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Convert hex pairs to normalized floats (0.0 - 1.0)
        mock_embedding = [
            float(int(text_hash[i:i+2], 16)) / 255.0
            for i in range(0, min(32, len(text_hash)), 2)
        ]

        # Pad to standard embedding size
        while len(mock_embedding) < self.EMBEDDING_DIMENSION:
            mock_embedding.append(0.0)

        # Truncate to exact dimension
        return mock_embedding[:self.EMBEDDING_DIMENSION]
