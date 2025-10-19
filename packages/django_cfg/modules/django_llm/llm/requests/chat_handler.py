"""
Chat request handler for LLM client.

Handles chat completion requests with caching and response building.
"""

import logging
import time
from typing import TYPE_CHECKING, Dict, List, Optional

from ..models import ChatCompletionResponse
from ..providers import ConfigBuilder

if TYPE_CHECKING:
    from ..providers import ProviderManager
    from ..responses import ResponseBuilder
    from ..stats import StatsManager
    from .cache_manager import RequestCacheManager

logger = logging.getLogger(__name__)


class ChatRequestHandler:
    """Handles chat completion requests with caching."""

    def __init__(
        self,
        provider_manager: 'ProviderManager',
        cache_manager: 'RequestCacheManager',
        stats_manager: 'StatsManager',
        response_builder: 'ResponseBuilder',
        tokenizer
    ):
        """
        Initialize chat request handler.

        Args:
            provider_manager: Provider manager instance
            cache_manager: Cache manager instance
            stats_manager: Stats manager instance
            response_builder: Response builder instance
            tokenizer: Tokenizer instance
        """
        self.provider_manager = provider_manager
        self.cache_manager = cache_manager
        self.stats_manager = stats_manager
        self.response_builder = response_builder
        self.tokenizer = tokenizer

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
        Execute chat completion with caching.

        Args:
            messages: List of chat messages
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Temperature for generation
            response_format: Response format (e.g., "json")
            **kwargs: Additional parameters

        Returns:
            Chat completion response

        Raises:
            RuntimeError: If client is not initialized or request fails
        """
        # Get client and provider
        client = self.provider_manager.primary_client
        provider = self.provider_manager.primary_provider

        if not client:
            raise RuntimeError("OpenAI client not initialized")

        # Use default model if needed
        if model is None:
            model = ConfigBuilder.get_default_model(provider)

        # Prepare API model (remove prefix for OpenAI)
        api_model = self._prepare_api_model(model, provider)

        # Check cache
        cached_response = self.cache_manager.get_cached_chat(
            messages, model, max_tokens, temperature, response_format, **kwargs
        )
        if cached_response:
            self.stats_manager.record_cache_hit()
            return cached_response

        self.stats_manager.record_cache_miss()
        self.stats_manager.record_request()

        # Estimate tokens
        estimated_tokens = self.tokenizer.count_messages_tokens(messages, model)
        logger.debug(f"Estimated input tokens: {estimated_tokens}")

        # Make API call
        start_time = time.time()
        try:
            api_response = self._make_api_call(
                client, api_model, messages, max_tokens, temperature, response_format, **kwargs
            )
            processing_time = time.time() - start_time

            # Build response object
            completion_response = self.response_builder.build_chat_response(
                api_response, model, provider, response_format, processing_time
            )

            # Cache response
            self.cache_manager.cache_chat_response(
                completion_response, messages, model, max_tokens, temperature, response_format, **kwargs
            )

            # Update stats
            self.stats_manager.record_success(
                tokens=completion_response.tokens_used,
                cost=completion_response.cost_usd,
                model=model,
                provider=provider
            )

            return completion_response

        except Exception as e:
            self.stats_manager.record_failure()
            logger.error(f"Chat completion failed: {e}")
            raise

    def _prepare_api_model(self, model: str, provider: str) -> str:
        """
        Prepare model name for API call.

        For OpenAI, remove provider prefix if present.

        Args:
            model: Model name
            provider: Provider name

        Returns:
            API-ready model name
        """
        api_model = model
        if provider == "openai" and model.startswith("openai/"):
            api_model = model.replace("openai/", "")
        return api_model

    def _make_api_call(
        self,
        client,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int],
        temperature: Optional[float],
        response_format: Optional[str],
        **kwargs
    ):
        """
        Make actual API call.

        Args:
            client: OpenAI client
            model: Model to use
            messages: Chat messages
            max_tokens: Max tokens
            temperature: Temperature
            response_format: Response format
            **kwargs: Additional parameters

        Returns:
            API response
        """
        params = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        # Add optional parameters
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        if temperature is not None:
            params["temperature"] = temperature
        if response_format:
            params["response_format"] = {"type": response_format}

        # Add any additional kwargs
        params.update(kwargs)

        logger.debug(f"Making chat completion request with model: {model}")
        return client.chat.completions.create(**params)
