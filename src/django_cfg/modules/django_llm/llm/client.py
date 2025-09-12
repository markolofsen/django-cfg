"""
LLM Client for django_llm.

Universal LLM client supporting multiple providers with caching and token optimization.
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import tiktoken
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai import (
    OpenAIError,
    RateLimitError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
)

from .cache import LLMCache
from .models_cache import ModelsCache, ModelInfo

logger = logging.getLogger(__name__)


class LLMClient:
    """Universal LLM client with caching and token optimization."""
    
    def __init__(
        self,
        provider: str = "openrouter",
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        cache_ttl: int = 3600,
        max_cache_size: int = 1000,
        models_cache_ttl: int = 86400,
        config: Optional[Any] = None
    ):
        """
        Initialize LLM client.
        
        Args:
            provider: Provider name (openrouter, openai, etc.)
            api_key: API key for the provider
            cache_dir: Cache directory path
            cache_ttl: Cache TTL in seconds
            max_cache_size: Maximum cache size
            models_cache_ttl: Models cache TTL in seconds (default: 24 hours)
            config: DjangoConfig instance for getting headers and settings
        """
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.cache = LLMCache(cache_dir=cache_dir, ttl=cache_ttl, max_size=max_cache_size)
        self.django_config = config
        
        # Initialize models cache for OpenRouter
        if self.provider == "openrouter":
            self.models_cache = ModelsCache(
                api_key=self.api_key,
                cache_dir=cache_dir,
                cache_ttl=models_cache_ttl
            )
        else:
            self.models_cache = None
        
        # Initialize tiktoken encoders
        self.encoders = {}
        
        # Get provider configuration with config-based headers
        self.provider_config = self._get_provider_config()
        
        # Initialize OpenAI client
        self.client = OpenAI(
            base_url=self.provider_config["base_url"],
            api_key=self.api_key,
            default_headers=self.provider_config.get("headers", {})
        )
        
        # Default models for each provider
        self.default_models = {
            "openrouter": "openai/gpt-4o-mini",
            "openai": "gpt-4o-mini"
        }
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'model_usage': {},
            'provider_usage': {}
        }
    
    def _get_api_key(self) -> str:
        """Get API key from environment."""
        import os
        env_var = f"{self.provider.upper()}_API_KEY"
        api_key = os.getenv(env_var)
        if not api_key:
            raise ValueError(f"API key not found. Set {env_var} environment variable.")
        return api_key
    
    def _get_provider_config(self) -> Dict[str, Any]:
        """Get provider configuration with config-based headers."""
        base_configs = {
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "headers": {}
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "headers": {}
            }
        }
        
        if self.provider not in base_configs:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        config = base_configs[self.provider].copy()

        site_url = getattr(self.django_config, 'site_url', 'https://unrealos.com')
        project_name = getattr(self.django_config, 'project_name', 'UnrealOS LLM Client')
        
        # Get headers from django config if available
        if self.django_config:
            if self.provider == "openrouter":
                # Get site URL and project name from config like in django_email
                
                config["headers"].update({
                    "HTTP-Referer": site_url,
                    "X-Title": project_name
                })
            
            # Add any custom headers from LLM config
            if hasattr(self.django_config, 'llm') and self.django_config.llm:
                llm_config = self.django_config.llm
                if hasattr(llm_config, 'custom_headers'):
                    config["headers"].update(llm_config.custom_headers)
        else:
            # Fallback headers if no config
            if self.provider == "openrouter":
                config["headers"].update({
                    "HTTP-Referer": site_url,
                    "X-Title": project_name
                })
        
        return config

    def _get_encoder(self, model: str):
        """Get tiktoken encoder for model."""
        if model not in self.encoders:
            try:
                # Map model names to encoding names
                encoding_name = self._get_encoding_name(model)
                self.encoders[model] = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                logger.warning(f"Failed to get encoder for {model}, using cl100k_base: {e}")
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        
        return self.encoders[model]
    
    def _get_encoding_name(self, model: str) -> str:
        """Get encoding name for model."""
        # GPT-4 and GPT-3.5 models use cl100k_base
        if any(name in model.lower() for name in ["gpt-4", "gpt-3.5", "gpt-4o"]):
            return "cl100k_base"
        # GPT-2 models use gpt2
        elif "gpt-2" in model.lower():
            return "gpt2"
        # Default to cl100k_base for most modern models
        else:
            return "cl100k_base"
    
    def count_tokens(self, text: str, model: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            model: Model name for encoding
            
        Returns:
            Number of tokens
        """
        encoder = self._get_encoder(model)
        return len(encoder.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]], model: str) -> int:
        """
        Count total tokens in messages.
        
        Args:
            messages: List of chat messages
            model: Model name for encoding
            
        Returns:
            Total number of tokens
        """
        total_tokens = 0
        
        for message in messages:
            # Format message as it would be sent to API
            role = message.get('role', 'user')
            content = message.get('content', '')
            formatted_message = f"{role}\n{content}"
            total_tokens += self.count_tokens(formatted_message, model)
        
        # Add overhead for message formatting
        total_tokens += len(messages) * 4  # Rough estimate for message overhead
        
        return total_tokens
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
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
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        # Use default model if not specified
        if model is None:
            model = self.default_models[self.provider]
        
        # Generate cache key
        request_hash = self.cache.generate_request_hash(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format=response_format,
            **kwargs
        )
        
        # Check cache
        cached_response = self.cache.get_response(request_hash)
        if cached_response:
            logger.debug("Cache hit for chat completion")
            self.stats['cache_hits'] += 1
            return cached_response
        
        self.stats['cache_misses'] += 1
        self.stats['total_requests'] += 1
        
        # Estimate tokens before API call
        estimated_input_tokens = self.count_messages_tokens(messages, model)
        logger.debug(f"Estimated input tokens: {estimated_input_tokens}")
        
        # Make API call
        start_time = time.time()
        try:
            # Prepare parameters
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
            
            # Make request
            response: ChatCompletion = self.client.chat.completions.create(**params)
            
            # Calculate processing time and cost
            processing_time = time.time() - start_time
            tokens_used = response.usage.total_tokens if response.usage else 0
            usage_dict = response.usage.model_dump() if response.usage else {'total_tokens': 0, 'prompt_tokens': 0, 'completion_tokens': 0}
            cost_usd = self._calculate_cost(usage_dict, model)
            
            # Extract content
            content = response.choices[0].message.content if response.choices else ""
            
            # Try to extract JSON if response_format was "json"
            extracted_json = None
            if response_format == "json" and content:
                extracted_json = self._extract_json_from_response(content)
            
            # Create response object
            completion_response = {
                'id': response.id,
                'model': response.model,
                'created': datetime.fromtimestamp(response.created).isoformat(),
                'choices': [choice.model_dump() for choice in response.choices] if response.choices else [],
                'usage': response.usage.model_dump() if response.usage else None,
                'finish_reason': response.choices[0].finish_reason if response.choices else None,
                'content': content,
                'tokens_used': tokens_used,
                'cost_usd': cost_usd,
                'processing_time': processing_time,
                'extracted_json': extracted_json
            }
            
            # Cache the response
            self.cache.set_response(request_hash, completion_response, model)
            
            # Update stats
            self.stats['successful_requests'] += 1
            self.stats['total_tokens_used'] += tokens_used
            self.stats['total_cost_usd'] += cost_usd
            self.stats['model_usage'][model] = self.stats['model_usage'].get(model, 0) + 1
            self.stats['provider_usage'][self.provider] = self.stats['provider_usage'].get(self.provider, 0) + 1
            
            return completion_response
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Chat completion failed: {e}")
            raise
    
    def _calculate_cost(self, usage: Dict[str, int], model: str) -> float:
        """Calculate cost based on usage and model using dynamic pricing."""
        # Try to get cost from models cache first
        if self.models_cache:
            try:
                cost = self.models_cache.calculate_cost_from_usage(model, usage)
                if cost is not None:
                    logger.debug(f"Using dynamic pricing for {model}: ${cost:.6f}")
                    return cost
            except Exception as e:
                logger.warning(f"Failed to calculate cost from models cache: {e}")
        
        # Fallback to hardcoded costs for common models
        total_tokens = usage.get('total_tokens', 0)
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        
        # Hardcoded costs per 1M tokens (fallback only)
        fallback_costs = {
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.6},
            "gpt-4o": {"prompt": 5.0, "completion": 15.0},
            "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
            "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
            "claude-3-sonnet": {"prompt": 3.0, "completion": 15.0},
            "claude-3-opus": {"prompt": 15.0, "completion": 75.0}
        }
        
        # Find matching model cost
        for model_pattern, costs in fallback_costs.items():
            if model_pattern in model.lower():
                prompt_cost = (prompt_tokens / 1_000_000) * costs["prompt"]
                completion_cost = (completion_tokens / 1_000_000) * costs["completion"]
                total_cost = prompt_cost + completion_cost
                logger.debug(f"Using fallback pricing for {model}: ${total_cost:.6f}")
                return total_cost
        
        # Default cost (using total tokens with average rate)
        default_cost = (total_tokens / 1_000_000) * 0.5
        logger.debug(f"Using default pricing for {model}: ${default_cost:.6f}")
        return default_cost
    
    def _extract_json_from_response(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from response content.
        
        Args:
            content: Response content from LLM
            
        Returns:
            Extracted JSON dict or None if no valid JSON found
        """
        try:
            # First try to parse as direct JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            import re
            
            # Look for JSON blocks
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'(\{.*?\})',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue
            
            return None
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get available models (placeholder - would need provider-specific implementation)."""
        # This would need to be implemented per provider
        return [
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai"},
            {"id": "openai/gpt-4o", "name": "GPT-4o", "provider": "openai"},
            {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "provider": "anthropic"},
        ]
    
    def refresh_models(self) -> bool:
        """Refresh available models (placeholder)."""
        # This would need to be implemented per provider
        return True
    
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
        # Try to use models cache first
        if self.models_cache:
            try:
                cost = self.models_cache.get_model_cost_estimate(model, input_tokens, output_tokens)
                if cost is not None:
                    return cost
            except Exception as e:
                logger.warning(f"Failed to estimate cost from models cache: {e}")
        
        # Fallback to internal calculation
        usage_dict = {
            'total_tokens': input_tokens + output_tokens,
            'prompt_tokens': input_tokens,
            'completion_tokens': output_tokens
        }
        return self._calculate_cost(usage_dict, model)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.stats.copy()
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information."""
        return {
            "provider": self.provider,
            "base_url": self.provider_config["base_url"],
            "headers": self.provider_config.get("headers", {}),
            "default_model": self.default_models.get(self.provider),
            "cache_info": self.cache.get_cache_info()
        }
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear_cache()
    
    # Models cache methods
    async def fetch_models(self, force_refresh: bool = False) -> Dict[str, ModelInfo]:
        """
        Fetch available models with pricing information.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            Dictionary of model_id -> ModelInfo
        """
        if not self.models_cache:
            logger.warning("Models cache not available for this provider")
            return {}
        
        return await self.models_cache.fetch_models(force_refresh=force_refresh)
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        if not self.models_cache:
            return None
        
        return self.models_cache.get_model(model_id)
    
    def get_models_by_price(self, 
                           min_price: float = 0.0, 
                           max_price: float = float('inf')) -> List[ModelInfo]:
        """Get models within a price range"""
        if not self.models_cache:
            return []
        
        return self.models_cache.get_models_by_price_range(min_price, max_price)
    
    def get_free_models(self) -> List[ModelInfo]:
        """Get all free models"""
        if not self.models_cache:
            return []
        
        return self.models_cache.get_free_models()
    
    def get_budget_models(self, max_price: float = 1.0) -> List[ModelInfo]:
        """Get budget models"""
        if not self.models_cache:
            return []
        
        return self.models_cache.get_budget_models(max_price)
    
    def get_premium_models(self, min_price: float = 10.0) -> List[ModelInfo]:
        """Get premium models"""
        if not self.models_cache:
            return []
        
        return self.models_cache.get_premium_models(min_price)
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """Search models by name, description, or tags"""
        if not self.models_cache:
            return []
        
        return self.models_cache.search_models(query)
    
    def get_models_summary(self) -> Dict[str, Any]:
        """Get summary of available models"""
        if not self.models_cache:
            return {"error": "Models cache not available for this provider"}
        
        return self.models_cache.get_models_summary()
    
    def get_models_cache_info(self) -> Dict[str, Any]:
        """Get models cache information"""
        if not self.models_cache:
            return {"error": "Models cache not available for this provider"}
        
        return self.models_cache.get_cache_info()
    
    def clear_models_cache(self):
        """Clear the models cache"""
        if self.models_cache:
            self.models_cache.clear_cache()
        logger.info("LLM client cache cleared")
