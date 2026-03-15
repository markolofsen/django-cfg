"""
Cache manager for LLM requests.

Manages caching of chat and embedding requests.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..cache import LLMCache
from ..models import ChatCompletionResponse, EmbeddingResponse

logger = logging.getLogger(__name__)


class RequestCacheManager:
    """Manages caching for LLM requests."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
        max_cache_size: int = 1000
    ):
        """
        Initialize cache manager.

        Args:
            cache_dir: Cache directory path
            cache_ttl: Cache TTL in seconds
            max_cache_size: Maximum cache size
        """
        self.cache = LLMCache(
            cache_dir=cache_dir,
            ttl=cache_ttl,
            max_size=max_cache_size
        )

    def get_cached_chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[str] = None,
        **kwargs
    ) -> Optional[ChatCompletionResponse]:
        """
        Get cached chat completion response.

        Args:
            messages: Chat messages
            model: Model used
            max_tokens: Max tokens
            temperature: Temperature
            response_format: Response format
            **kwargs: Additional parameters

        Returns:
            Cached response or None
        """
        request_hash = self.cache.generate_request_hash(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs
        )

        cached_response = self.cache.get_response(request_hash)
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
        response_format: Optional[str] = None,
        **kwargs
    ):
        """
        Cache chat completion response.

        Args:
            response: Response to cache
            messages: Chat messages
            model: Model used
            max_tokens: Max tokens
            temperature: Temperature
            response_format: Response format
            **kwargs: Additional parameters
        """
        request_hash = self.cache.generate_request_hash(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs
        )

        self.cache.set_response(request_hash, response.model_dump(), model)
        logger.debug("Cached chat completion response")

    def get_cached_embedding(
        self,
        text: str,
        model: str
    ) -> Optional[EmbeddingResponse]:
        """
        Get cached embedding response.

        Args:
            text: Input text
            model: Model used

        Returns:
            Cached response or None
        """
        request_hash = self.cache.generate_request_hash(
            messages=[{"role": "user", "content": text}],
            model=model,
            task="embedding"
        )

        cached_response = self.cache.get_response(request_hash)
        if cached_response:
            logger.debug("Cache hit for embedding generation")
            return EmbeddingResponse(**cached_response)

        return None

    def cache_embedding_response(
        self,
        response: EmbeddingResponse,
        text: str,
        model: str
    ):
        """
        Cache embedding response.

        Args:
            response: Response to cache
            text: Input text
            model: Model used
        """
        request_hash = self.cache.generate_request_hash(
            messages=[{"role": "user", "content": text}],
            model=model,
            task="embedding"
        )

        self.cache.set_response(request_hash, response.model_dump(), model)
        logger.debug("Cached embedding response")

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information."""
        return self.cache.get_cache_info()

    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear_cache()
