"""
Mock embedder — a keyless-dev stopgap, NOT an embedding.

It returns 1536 deterministic MD5-derived floats. They have the shape of an
embedding and none of the meaning: cosine similarity between two mock vectors is
noise, so any search built on them silently returns garbage.

**Two guards keep that garbage from escaping this file**, because a vector that
looks valid is far more dangerous than one that is obviously missing:

1. Every response carries :data:`MOCK_WARNING` in ``warning``. That field is the
   contract — :func:`is_mock_embedding` is how the rest of the system asks.
2. The handler NEVER caches a mock response, so one keyless run cannot poison the
   cache for every run that follows (a mock cached under a text/model key would
   still be served after the key was restored).

Callers that PERSIST a vector (a pgvector column) must refuse a mock rather than
store it. `modules/django_llm/features/embeddings.py` enforces this at the public
seam, so no app has to remember to.
"""

import hashlib
import logging
import time

from ..registry.pricing import calculate_embedding_cost
from ..core.types import EmbeddingResponse

logger = logging.getLogger(__name__)

#: The marker on every mock response. Load-bearing — the handler keys its
#: no-cache rule off it, and `is_mock_embedding` is the public predicate.
MOCK_WARNING = "Mock embedding — no real provider key. NOT semantically valid."


def is_mock_embedding(response) -> bool:
    """True iff this response is MD5 noise rather than a real embedding.

    Anything that writes a vector to a pgvector column must check this. Both the
    persisted vector and any similarity computed from it would otherwise be
    meaningless, and — worse — indistinguishable from a working system.
    """
    return bool(getattr(response, "warning", None)) and MOCK_WARNING in response.warning


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
        Generate a mock embedding (MD5-derived, deterministic, MEANINGLESS).

        Reached only when no real embedding provider is configured. The result is
        stamped with :data:`MOCK_WARNING` so the handler declines to cache it and
        persisting callers decline to store it. See this module's docstring.

        Args:
            text: Text to generate embedding for
            model: Model name (used for cost estimation)

        Returns:
            EmbeddingResponse with a mock vector and ``warning`` set.
        """
        start_time = time.time()

        logger.warning(
            "Mock embedding for model %s — no real provider key. This vector is "
            "MD5 noise: it will not be cached and must not be persisted.",
            model,
        )

        # Create mock embedding from text hash
        mock_embedding = self._create_mock_vector(text)

        # Estimate tokens and cost
        tokens_used = len(text.split())  # Rough estimate
        cost = calculate_embedding_cost(tokens_used, model, self.models_cache)

        response_time = time.time() - start_time

        return EmbeddingResponse(
            embedding=mock_embedding,
            tokens=tokens_used,
            cost=cost,
            model=model,
            text_length=len(text),
            dimension=len(mock_embedding),
            response_time=response_time,
            warning=MOCK_WARNING,
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
