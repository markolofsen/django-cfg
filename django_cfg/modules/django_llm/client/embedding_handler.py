"""
Embedding request handler for LLM client.

Handles embedding generation requests with provider-specific strategies.
"""

import logging
from typing import TYPE_CHECKING, Optional

from ..core.types import EmbeddingResponse
from ..embeddings.mock_embedder import is_mock_embedding

if TYPE_CHECKING:
    from ..embeddings import MockEmbedder, OpenAIEmbedder, OpenRouterEmbedder
    from ..providers import ProviderManager, ProviderSelector
    from .stats import StatsManager
    from ..storage.cache_manager import RequestCacheManager

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
        mock_embedder: 'MockEmbedder',
        openrouter_embedder: "Optional[OpenRouterEmbedder]" = None,
    ):
        """
        Initialize embedding request handler.

        Args:
            provider_manager: Provider manager instance
            provider_selector: Provider selector instance
            cache_manager: Cache manager instance
            stats_manager: Stats manager instance
            openai_embedder: OpenAI embedder instance
            mock_embedder: Mock embedder instance (only used when no
                real embedding provider is available)
            openrouter_embedder: OpenRouter embedder instance — real
                embeddings via OpenRouter's OpenAI-compatible endpoint.
        """
        self.provider_manager = provider_manager
        self.provider_selector = provider_selector
        self.cache_manager = cache_manager
        self.stats_manager = stats_manager
        self.openai_embedder = openai_embedder
        self.openrouter_embedder = openrouter_embedder
        self.mock_embedder = mock_embedder

    def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002",
        *,
        dimensions: int | None = None,
    ) -> EmbeddingResponse:
        """
        Generate embedding with provider-specific logic.

        Routes to a REAL embedder: OpenAI when the provider is OpenAI,
        OpenRouter (OpenAI-compatible ``/embeddings``) when the provider
        is OpenRouter. The MD5 mock is a last-resort fallback only when
        neither real path is available (e.g. no provider client) — it
        must never silently stand in for a real embedding in production.

        Args:
            text: Text to generate embedding for
            model: Embedding model to use
            dimensions: Optional output dimension (forwarded to the
                OpenRouter/OpenAI v3 models; e.g. 1536 for -3-large).

        Returns:
            Embedding response with vector and metadata

        Raises:
            RuntimeError: If embedding generation fails
        """
        # Cache key includes the dimension so a 1536 and a 3072 request
        # for the same text/model don't collide.
        cache_model = model if dimensions is None else f"{model}@{dimensions}"
        cached_response = self.cache_manager.get_cached_embedding(text, cache_model)
        if cached_response:
            self.stats_manager.record_cache_hit()
            return cached_response

        self.stats_manager.record_cache_miss()
        self.stats_manager.record_request()

        # Get best provider for embedding
        provider = self.provider_selector.get_provider_for_task("embedding")

        try:
            client = self.provider_manager.get_client(provider)

            if provider == "openrouter" and self.openrouter_embedder is not None:
                logger.debug("Using OpenRouter embedder for model %s", model)
                result = self.openrouter_embedder.generate(
                    client, text, model, dimensions=dimensions,
                )
            elif provider == "openai" and client is not None:
                logger.debug("Using OpenAI embedder for model %s", model)
                result = self.openai_embedder.generate(client, text, model)
            else:
                # Last-resort fallback — only when no real provider client
                # exists. Logs a warning inside MockEmbedder.
                logger.warning(
                    "No real embedding provider for %r — falling back to mock",
                    provider,
                )
                result = self.mock_embedder.generate(text, model)

            # Cache response — EXCEPT a mock. A mock vector cached under a
            # (text, model) key outlives the missing key that produced it: it
            # would still be served after real credentials were restored, and
            # nothing downstream could tell it from a real embedding. A cache
            # miss is recoverable; a poisoned cache is not.
            if not is_mock_embedding(result):
                self.cache_manager.cache_embedding_response(result, text, cache_model)

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

    def generate_embeddings(
        self,
        texts: list[str],
        model: str = "text-embedding-ada-002",
        *,
        dimensions: int | None = None,
    ) -> list[EmbeddingResponse]:
        """Embed MANY texts, sending only the cache misses, in ONE request.

        Same cache keys, same stats, same provider routing as
        :meth:`generate_embedding` — this is that method's batch twin, not a
        second embedding path. Returns one response per input, in input order.

        Only the OpenRouter embedder has a real batch endpoint wired up (it is
        the project's provider). Every other route falls back to a serial loop,
        which is exactly the old behaviour — correct, just not fast.

        Args:
            texts: Texts to embed. Must not contain empty strings; an empty text
                has no embedding, and callers that may produce one must filter it
                out and re-align (``features.embeddings.embed_texts`` does this).
            model: Embedding model to use.
            dimensions: Optional output dimension.

        Raises:
            RuntimeError: If embedding generation fails.
            ValueError: If any text is empty.
        """
        if not texts:
            return []
        if any(not t for t in texts):
            raise ValueError(
                "generate_embeddings does not accept empty strings — an empty "
                "text has no embedding. Filter and re-align before calling."
            )

        cache_model = model if dimensions is None else f"{model}@{dimensions}"

        # Resolve from cache first. Only what is left over costs a round-trip —
        # this is what makes a re-run of a backfill nearly free.
        resolved: list[EmbeddingResponse | None] = []
        missing_indices: list[int] = []
        for index, text in enumerate(texts):
            cached = self.cache_manager.get_cached_embedding(text, cache_model)
            if cached:
                self.stats_manager.record_cache_hit()
                resolved.append(cached)
            else:
                self.stats_manager.record_cache_miss()
                resolved.append(None)
                missing_indices.append(index)

        if not missing_indices:
            return [item for item in resolved if item is not None]

        missing_texts = [texts[i] for i in missing_indices]
        self.stats_manager.record_request()
        provider = self.provider_selector.get_provider_for_task("embedding")

        try:
            client = self.provider_manager.get_client(provider)

            if provider == "openrouter" and self.openrouter_embedder is not None:
                logger.debug(
                    "Batch-embedding %d texts via OpenRouter (model=%s)",
                    len(missing_texts), model,
                )
                fresh = self.openrouter_embedder.generate_batch(
                    client, missing_texts, model, dimensions=dimensions,
                )
            elif provider == "openai" and client is not None:
                # The OpenAI embedder has no batch method (and no `dimensions`
                # parameter). Serial, as before — no provider is worse off than
                # it was, and the one we actually use is faster.
                fresh = [
                    self.openai_embedder.generate(client, text, model)
                    for text in missing_texts
                ]
            else:
                logger.warning(
                    "No real embedding provider for %r — falling back to mock",
                    provider,
                )
                fresh = [
                    self.mock_embedder.generate(text, model) for text in missing_texts
                ]

            for index, text, result in zip(missing_indices, missing_texts, fresh):
                # Same rule as the scalar path: a mock never enters the cache.
                if not is_mock_embedding(result):
                    self.cache_manager.cache_embedding_response(result, text, cache_model)
                resolved[index] = result

            self.stats_manager.record_success(
                tokens=sum(item.tokens for item in fresh),
                cost=sum(item.cost for item in fresh),
                model=model,
                provider=provider,
            )

            return [item for item in resolved if item is not None]

        except Exception as e:
            self.stats_manager.record_failure()
            error_msg = f"Batch embedding generation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
