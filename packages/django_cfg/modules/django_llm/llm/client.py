"""
LLM Client for django_llm.

Universal LLM client supporting multiple providers with caching and token optimization.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...base import BaseCfgModule
from .embeddings import MockEmbedder, OpenAIEmbedder
from .extractor import JSONExtractor
from .models import (
    ChatCompletionResponse,
    EmbeddingResponse,
)
from .models_api import ModelsQueryAPI
from .models_cache import ModelInfo, ModelsCache

# Import new components
from .providers import ProviderManager, ProviderSelector
from .requests import ChatRequestHandler, EmbeddingRequestHandler, RequestCacheManager
from .responses import ResponseBuilder
from .stats import StatsManager
from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class LLMClient(BaseCfgModule):
    """Universal LLM client with caching and token optimization."""

    def __init__(
        self,
        apikey_openrouter: Optional[str] = None,
        apikey_openai: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
        max_cache_size: int = 1000,
        models_cache_ttl: int = 86400,
        config: Optional[Any] = None,
        preferred_provider: Optional[str] = None
    ):
        """
        Initialize LLM client.

        Args:
            apikey_openrouter: API key for OpenRouter (auto-detected if not provided)
            apikey_openai: API key for OpenAI (auto-detected if not provided)
            cache_dir: Cache directory path
            cache_ttl: Cache TTL in seconds
            max_cache_size: Maximum cache size
            models_cache_ttl: Models cache TTL in seconds (default: 24 hours)
            config: DjangoConfig instance for getting headers and settings
            preferred_provider: Preferred provider ("openai" or "openrouter").
                               If None, defaults to "openai" for embeddings, "openrouter" for chat
        """
        super().__init__()

        # Auto-detect API keys from config if not provided
        django_config = self.get_config()
        if django_config:
            if apikey_openai is None:
                # Try new api_keys system first, then fallback to old attribute
                if hasattr(django_config, 'api_keys') and django_config.api_keys:
                    apikey_openai = django_config.api_keys.get_openai_key()
                else:
                    apikey_openai = getattr(django_config, 'openai_api_key', None)

            if apikey_openrouter is None:
                # Try new api_keys system first
                if hasattr(django_config, 'api_keys') and django_config.api_keys:
                    apikey_openrouter = django_config.api_keys.get_openrouter_key()

        # Initialize provider management
        self.provider_manager = ProviderManager(
            apikey_openrouter=apikey_openrouter,
            apikey_openai=apikey_openai,
            preferred_provider=preferred_provider,
            django_config=config
        )
        self.provider_selector = ProviderSelector(self.provider_manager)

        # Initialize cache and stats
        self.cache_manager = RequestCacheManager(
            cache_dir=cache_dir,
            cache_ttl=cache_ttl,
            max_cache_size=max_cache_size
        )
        self.stats_manager = StatsManager()

        # Initialize models cache if OpenRouter available
        self.models_cache = None
        if apikey_openrouter:
            self.models_cache = ModelsCache(
                api_key=apikey_openrouter,
                cache_dir=cache_dir,
                cache_ttl=models_cache_ttl
            )

        # Initialize tokenizer and utilities
        self.tokenizer = Tokenizer()
        self.json_extractor = JSONExtractor()

        # Initialize response builder
        self.response_builder = ResponseBuilder(
            models_cache=self.models_cache,
            json_extractor=self.json_extractor
        )

        # Initialize embedding strategies
        self.openai_embedder = OpenAIEmbedder(models_cache=self.models_cache)
        self.mock_embedder = MockEmbedder(models_cache=self.models_cache)

        # Initialize request handlers
        self.chat_handler = ChatRequestHandler(
            provider_manager=self.provider_manager,
            cache_manager=self.cache_manager,
            stats_manager=self.stats_manager,
            response_builder=self.response_builder,
            tokenizer=self.tokenizer
        )

        self.embedding_handler = EmbeddingRequestHandler(
            provider_manager=self.provider_manager,
            provider_selector=self.provider_selector,
            cache_manager=self.cache_manager,
            stats_manager=self.stats_manager,
            openai_embedder=self.openai_embedder,
            mock_embedder=self.mock_embedder
        )

        # Initialize models query API
        self.models_api = ModelsQueryAPI(models_cache=self.models_cache)

        logger.info(
            f"LLMClient initialized with primary provider: "
            f"{self.provider_manager.primary_provider}"
        )

    # Token counting (delegate to tokenizer)
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text using tokenizer."""
        return self.tokenizer.count_tokens(text, model)

    def count_messages_tokens(self, messages: List[Dict[str, str]], model: str) -> int:
        """Count total tokens in messages using tokenizer."""
        return self.tokenizer.count_messages_tokens(messages, model)

    # Chat completion (delegate to chat handler)
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[str] = None,
        **kwargs
    ) -> ChatCompletionResponse:
        """
        Send chat completion request.

        Args:
            messages: List of chat messages
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Temperature for generation
            response_format: Response format (e.g., "json")
            **kwargs: Additional parameters

        Returns:
            Chat completion response
        """
        return self.chat_handler.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs
        )

    # Embedding generation (delegate to embedding handler)
    def generate_embedding(
        self,
        text: str,
        model: str = "text-embedding-ada-002"
    ) -> EmbeddingResponse:
        """
        Generate embedding for text.

        Args:
            text: Text to generate embedding for
            model: Embedding model to use

        Returns:
            Dictionary with embedding data and metadata
        """
        return self.embedding_handler.generate_embedding(text=text, model=model)

    # Cost estimation
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate cost for a model.

        Args:
            model: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        from .costs import estimate_cost
        return estimate_cost(model, input_tokens, output_tokens, self.models_cache)

    # Statistics and info (delegate to stats manager)
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.stats_manager.get_stats()

    def get_client_info(self) -> Dict[str, Any]:
        """Get client information."""
        return {
            "primary_provider": self.provider_manager.primary_provider,
            "available_providers": self.provider_manager.get_available_providers(),
            "cache_info": self.cache_manager.get_cache_info(),
            "has_openrouter": self.provider_manager.has_provider("openrouter"),
            "has_openai": self.provider_manager.has_provider("openai")
        }

    def clear_cache(self):
        """Clear the cache."""
        self.cache_manager.clear_cache()

    # Models API delegation
    async def fetch_models(self, force_refresh: bool = False) -> Dict[str, ModelInfo]:
        """
        Fetch available models with pricing information.

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dictionary of model_id -> ModelInfo
        """
        return await self.models_api.fetch_models(force_refresh=force_refresh)

    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        return self.models_api.get_model_info(model_id)

    def get_models_by_price(
        self,
        min_price: float = 0.0,
        max_price: float = float('inf')
    ) -> List[ModelInfo]:
        """Get models within a price range."""
        return self.models_api.get_models_by_price(min_price, max_price)

    def get_free_models(self) -> List[ModelInfo]:
        """Get all free models."""
        return self.models_api.get_free_models()

    def get_budget_models(self, max_price: float = 1.0) -> List[ModelInfo]:
        """Get budget models."""
        return self.models_api.get_budget_models(max_price)

    def get_premium_models(self, min_price: float = 10.0) -> List[ModelInfo]:
        """Get premium models."""
        return self.models_api.get_premium_models(min_price)

    def search_models(self, query: str) -> List[ModelInfo]:
        """Search models by name, description, or tags."""
        return self.models_api.search_models(query)

    def get_models_summary(self) -> Dict[str, Any]:
        """Get summary of available models."""
        return self.models_api.get_models_summary()

    def get_models_cache_info(self) -> Dict[str, Any]:
        """Get models cache information."""
        return self.models_api.get_models_cache_info()

    def clear_models_cache(self):
        """Clear the models cache."""
        self.models_api.clear_models_cache()
