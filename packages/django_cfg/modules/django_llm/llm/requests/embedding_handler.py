"""
Embedding request handler for LLM client.

Handles embedding generation requests with provider-specific strategies.
"""

import logging
from typing import TYPE_CHECKING

from ..models import EmbeddingResponse

if TYPE_CHECKING:
    from ..embeddings import MockEmbedder, OpenAIEmbedder
    from ..providers import ProviderManager, ProviderSelector
    from ..stats import StatsManager
    from .cache_manager import RequestCacheManager

logger = logging.getLogger(__name__)


class EmbeddingRequestHandler:
    """Handles embedding generation requests."""

    def __init__(
        self,
        provider_manager: 'ProviderManager',
        provider_selector: 'ProviderSelector',
        cache_manager: 'RequestCacheManager',
        stats_manager: 'StatsManager',
        openai_embedder: 'OpenAIEmbedder',
        mock_embedder: 'MockEmbedder'
    ):
        """
        Initialize embedding request handler.

        Args:
            provider_manager: Provider manager instance
            provider_selector: Provider selector instance
            cache_manager: Cache manager instance
            stats_manager: Stats manager instance
            openai_embedder: OpenAI embedder instance
            mock_embedder: Mock embedder instance
        """
        self.provider_manager = provider_manager
        self.provider_selector = provider_selector
        self.cache_manager = cache_manager
        self.stats_manager = stats_manager
        self.openai_embedder = openai_embedder
        self.mock_embedder = mock_embedder

    def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> EmbeddingResponse:
        """
        Generate embedding with provider-specific logic.

        Uses real OpenAI embeddings when available, falls back to mock
        embeddings for providers without embedding support.

        Args:
            text: Text to generate embedding for
            model: Embedding model to use

        Returns:
            Embedding response with vector and metadata

        Raises:
            RuntimeError: If embedding generation fails
        """
        # Check cache
        cached_response = self.cache_manager.get_cached_embedding(text, model)
        if cached_response:
            self.stats_manager.record_cache_hit()
            return cached_response

        self.stats_manager.record_cache_miss()
        self.stats_manager.record_request()

        # Get best provider for embedding
        provider = self.provider_selector.get_provider_for_task("embedding")

        try:
            # Generate embedding using appropriate strategy
            if self.provider_selector.should_use_mock_embedding(provider):
                # Use mock embedder for OpenRouter
                logger.debug(f"Using mock embedder for provider: {provider}")
                result = self.mock_embedder.generate(text, model)
            else:
                # Use real OpenAI embeddings
                logger.debug(f"Using OpenAI embedder for provider: {provider}")
                client = self.provider_manager.get_client(provider)
                result = self.openai_embedder.generate(client, text, model)

            # Cache response
            self.cache_manager.cache_embedding_response(result, text, model)

            # Update stats
            self.stats_manager.record_success(
                tokens=result.tokens,
                cost=result.cost,
                model=model,
                provider=provider
            )

            return result

        except Exception as e:
            self.stats_manager.record_failure()
            error_msg = f"Embedding generation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
