"""
Cache manager for LLM requests.

The cache is **fail-open** — any backend error falls through to a live
call (get -> None, set -> no-op) so the cache can never break a real
request. Non-deterministic chat calls (``temperature > 0``) are never
cached: a hit would replay one arbitrary sample as if it were the answer.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache import LLMCache
from ..core.types import ChatCompletionResponse, EmbeddingResponse

logger = logging.getLogger(__name__)


def _is_cacheable_temperature(temperature: Optional[float]) -> bool:
    """Only deterministic calls are safe to cache.

    ``None`` (provider default) and ``0`` are treated as cacheable; any
    positive temperature makes the response non-deterministic.
    """
    return temperature is None or temperature <= 0


class RequestCacheManager:
    """Manages caching for LLM requests (fail-open)."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
        max_cache_size: int = 1000,
    ):
        self.cache = LLMCache(
            cache_dir=cache_dir,
            ttl=cache_ttl,
            max_size=max_cache_size,
        )

    def get_cached_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Any] = None,
        **kwargs,
    ) -> Optional[ChatCompletionResponse]:
        """Return a cached chat response, or None (on miss, skip, or error)."""
        if not _is_cacheable_temperature(temperature):
            return None
        try:
            request_hash = self.cache.generate_request_hash(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,
                **kwargs,
            )
            cached_response = self.cache.get_response(request_hash)
        except Exception as exc:
            logger.debug("Cache read skipped (fail-open): %s", exc)
            return None

        if cached_response:
            logger.debug("Cache hit for chat completion")
            return ChatCompletionResponse(**cached_response)
        return None

    def cache_chat_response(
        self,
        response: ChatCompletionResponse,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Any] = None,
        **kwargs,
    ) -> None:
        """Cache a chat response. No-op for non-deterministic calls or on error."""
        if not _is_cacheable_temperature(temperature):
            return
        try:
            request_hash = self.cache.generate_request_hash(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,
                **kwargs,
            )
            self.cache.set_response(request_hash, response.model_dump(), model)
            logger.debug("Cached chat completion response")
        except Exception as exc:
            logger.debug("Cache write skipped (fail-open): %s", exc)

    def get_cached_embedding(
        self,
        text: str,
        model: str,
    ) -> Optional[EmbeddingResponse]:
        """Return a cached embedding, or None. Embeddings are deterministic."""
        try:
            request_hash = self.cache.generate_request_hash(
                messages=[{"role": "user", "content": text}],
                model=model,
                task="embedding",
            )
            cached_response = self.cache.get_response(request_hash)
        except Exception as exc:
            logger.debug("Cache read skipped (fail-open): %s", exc)
            return None

        if cached_response:
            logger.debug("Cache hit for embedding generation")
            return EmbeddingResponse(**cached_response)
        return None

    def cache_embedding_response(
        self,
        response: EmbeddingResponse,
        text: str,
        model: str,
    ) -> None:
        """Cache an embedding response. No-op on error."""
        try:
            request_hash = self.cache.generate_request_hash(
                messages=[{"role": "user", "content": text}],
                model=model,
                task="embedding",
            )
            self.cache.set_response(request_hash, response.model_dump(), model)
            logger.debug("Cached embedding response")
        except Exception as exc:
            logger.debug("Cache write skipped (fail-open): %s", exc)

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information (empty dict on error)."""
        try:
            return self.cache.get_cache_info()
        except Exception as exc:
            logger.debug("Cache info unavailable (fail-open): %s", exc)
            return {}

    def clear_cache(self) -> None:
        """Clear the cache. No-op on error."""
        try:
            self.cache.clear_cache()
        except Exception as exc:
            logger.debug("Cache clear skipped (fail-open): %s", exc)
