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
from .costs import calculate_chat_cost, calculate_embedding_cost, estimate_cost
from .tokenizer import Tokenizer
from .extractor import JSONExtractor
from .models import (
    EmbeddingResponse, 
    ChatCompletionResponse, 
    TokenUsage, 
    ChatChoice,
    LLMStats,
    CostEstimate,
    ValidationResult,
    CacheInfo,
    LLMError
)
from ...base import BaseCfgModule

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
                apikey_openai = getattr(django_config, 'openai_api_key', None)
            # Add other API keys as needed
        
        # Store API keys and preferred provider
        self.apikey_openrouter = apikey_openrouter
        self.apikey_openai = apikey_openai
        self.preferred_provider = preferred_provider
        
        # Determine primary provider based on preference and available keys
        self.primary_provider = self._determine_primary_provider()
        self.primary_api_key = self._get_primary_api_key()
        
        self.cache = LLMCache(cache_dir=cache_dir, ttl=cache_ttl, max_size=max_cache_size)
        self.django_config = config
        
        # Initialize models cache for OpenRouter if available
        if self.apikey_openrouter:
            self.models_cache = ModelsCache(
                api_key=self.apikey_openrouter,
                cache_dir=cache_dir,
                cache_ttl=models_cache_ttl
            )
        else:
            self.models_cache = None
        
        # Initialize tokenizer and extractor
        self.tokenizer = Tokenizer()
        self.extractor = JSONExtractor()
        
        # Initialize clients for available providers
        self.clients = {}
        
        if self.apikey_openrouter:
            self.clients["openrouter"] = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.apikey_openrouter,
                default_headers=self._get_openrouter_headers()
            )
        
        if self.apikey_openai:
            self.clients["openai"] = OpenAI(
                api_key=self.apikey_openai
            )
        
        # Set primary client
        self.client = self.clients[self.primary_provider]
        
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

        site_url = getattr(self.django_config, 'site_url', 'https://djangocfg.com')
        project_name = getattr(self.django_config, 'project_name', 'Django CFG LLM Client')
        
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

    def _get_openrouter_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API."""
        headers = {}
        
        # Add site info from Django config if available
        if self.django_config:
            try:
                site_url = getattr(self.django_config, 'site_url', 'http://localhost:8000')
                project_name = getattr(self.django_config, 'project_name', 'Django CFG')
                headers.update({
                    "HTTP-Referer": site_url,
                    "X-Title": project_name
                })
            except Exception:
                pass
        
        return headers

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text using tokenizer."""
        return self.tokenizer.count_tokens(text, model)
    
    def count_messages_tokens(self, messages: List[Dict[str, str]], model: str) -> int:
        """Count total tokens in messages using tokenizer."""
        return self.tokenizer.count_messages_tokens(messages, model)
    
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
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        # Use default model if not specified
        if model is None:
            model = self.default_models[self.primary_provider]
        
        # For OpenAI, remove provider prefix if present
        api_model = model
        if self.primary_provider == "openai" and model.startswith("openai/"):
            api_model = model.replace("openai/", "")
        
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
            # Convert cached dict back to Pydantic model
            return ChatCompletionResponse(**cached_response)
        
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
                "model": api_model,
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
            cost_usd = calculate_chat_cost(usage_dict, model, self.models_cache)
            
            # Extract content
            content = response.choices[0].message.content if response.choices else ""
            
            # Try to extract JSON if response_format was "json"
            extracted_json = None
            if response_format == "json" and content:
                extracted_json = self.extractor.extract_json_from_response(content)
            
            # Create Pydantic response object
            completion_response = ChatCompletionResponse(
                id=response.id,
                model=response.model,
                created=datetime.fromtimestamp(response.created).isoformat(),
                choices=[
                    ChatChoice(
                        index=choice.index,
                        message=choice.message.model_dump() if hasattr(choice.message, 'model_dump') else choice.message,
                        finish_reason=choice.finish_reason
                    ) for choice in response.choices
                ] if response.choices else [],
                usage=TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                    completion_tokens=response.usage.completion_tokens if response.usage else 0,
                    total_tokens=response.usage.total_tokens if response.usage else tokens_used
                ) if response.usage else TokenUsage(total_tokens=tokens_used),
                finish_reason=response.choices[0].finish_reason if response.choices else None,
                content=content,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                processing_time=processing_time,
                extracted_json=extracted_json
            )
            
            # Cache the response (serialize to dict for caching)
            self.cache.set_response(request_hash, completion_response.model_dump(), model)
            
            # Update stats
            self.stats['successful_requests'] += 1
            self.stats['total_tokens_used'] += tokens_used
            self.stats['total_cost_usd'] += cost_usd
            self.stats['model_usage'][model] = self.stats['model_usage'].get(model, 0) + 1
            self.stats['provider_usage'][self.primary_provider] = self.stats['provider_usage'].get(self.primary_provider, 0) + 1
            
            return completion_response
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Chat completion failed: {e}")
            raise
    
    
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
        return estimate_cost(model, input_tokens, output_tokens, self.models_cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.stats.copy()
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information."""
        return {
            "primary_provider": self.primary_provider,
            "available_providers": list(self.clients.keys()),
            "default_models": self.default_models,
            "cache_info": self.cache.get_cache_info(),
            "has_openrouter": self.apikey_openrouter is not None,
            "has_openai": self.apikey_openai is not None
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
    
    def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> EmbeddingResponse:
        """
        Generate embedding for text.
        
        Args:
            text: Text to generate embedding for
            model: Embedding model to use
            
        Returns:
            Dictionary with embedding data and metadata
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        # Generate cache key for embedding
        request_hash = self.cache.generate_request_hash(
            messages=[{"role": "user", "content": text}],
            model=model,
            task="embedding"
        )
        
        # Check cache
        cached_response = self.cache.get_response(request_hash)
        if cached_response:
            logger.debug("Cache hit for embedding generation")
            self.stats['cache_hits'] += 1
            # Convert cached dict back to Pydantic model
            return EmbeddingResponse(**cached_response)
        
        self.stats['cache_misses'] += 1
        self.stats['total_requests'] += 1
        
        start_time = time.time()
        try:
            # Get the best provider for embedding task
            embedding_provider = self.get_provider_for_task("embedding")
            
            # For OpenRouter, we need to use a different model for embeddings
            # OpenRouter doesn't support OpenAI embedding models directly
            if embedding_provider == "openrouter":
                # Use a text generation model to simulate embeddings
                # This is a workaround since OpenRouter doesn't have embedding endpoints
                logger.warning("OpenRouter doesn't support embedding models, using text generation as fallback")
                
                # Create a simple embedding simulation using text generation
                messages = [
                    {"role": "system", "content": "Generate a numerical representation (embedding-like) for the following text. Return only numbers separated by commas."},
                    {"role": "user", "content": f"Text: {text[:500]}"}  # Limit text length
                ]
                
                # Use a cheap model for this
                chat_model = "openai/gpt-4o-mini"
                response = self.client.chat.completions.create(
                    model=chat_model,
                    messages=messages,
                    max_tokens=100,
                    temperature=0.0
                )
                
                # Create a mock embedding (this is not a real embedding!)
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()
                mock_embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 for i in range(0, min(32, len(text_hash)), 2)]
                
                # Pad to standard embedding size
                while len(mock_embedding) < 1536:
                    mock_embedding.append(0.0)
                mock_embedding = mock_embedding[:1536]
                
                tokens_used = len(text.split())  # Rough estimate
                cost = calculate_embedding_cost(tokens_used, model, self.models_cache)
                
                result = EmbeddingResponse(
                    embedding=mock_embedding,
                    tokens=tokens_used,
                    cost=cost,
                    model=model,
                    text_length=len(text),
                    dimension=len(mock_embedding),
                    response_time=time.time() - start_time,
                    warning="This is a mock embedding, not a real one. OpenRouter doesn't support embedding models."
                )
            else:
                # Use real OpenAI embedding API
                embedding_client = self.clients[embedding_provider]
                # For OpenAI, remove provider prefix if present
                api_model = model
                if embedding_provider == "openai" and model.startswith("openai/"):
                    api_model = model.replace("openai/", "")
                
                response = embedding_client.embeddings.create(
                    input=text,
                    model=api_model
                )
                
                # Extract embedding data
                embedding_data = response.data[0]
                embedding_vector = embedding_data.embedding
                
                # Calculate tokens and cost
                tokens_used = response.usage.total_tokens
                cost = calculate_embedding_cost(tokens_used, model, self.models_cache)
                
                result = EmbeddingResponse(
                    embedding=embedding_vector,
                    tokens=tokens_used,
                    cost=cost,
                    model=model,
                    text_length=len(text),
                    dimension=len(embedding_vector),
                    response_time=time.time() - start_time
                )
            
            # Update statistics
            self.stats['successful_requests'] += 1
            self.stats['total_tokens_used'] += result.tokens
            self.stats['total_cost_usd'] += result.cost
            
            # Cache the result (convert to dict for caching)
            self.cache.set_response(request_hash, result.model_dump(), model)
            
            logger.debug(f"Generated embedding: {result.tokens} tokens, ${result.cost:.6f}")
            return result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            error_msg = f"Embedding generation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    def _determine_primary_provider(self) -> str:
        """
        Determine primary provider based on preference and available keys.
        
        Returns:
            Primary provider name
        """
        # If preferred provider is explicitly set and available, use it
        if self.preferred_provider:
            if self.preferred_provider == "openai" and self.apikey_openai:
                return "openai"
            elif self.preferred_provider == "openrouter" and self.apikey_openrouter:
                return "openrouter"
            else:
                logger.warning(f"Preferred provider '{self.preferred_provider}' not available, falling back to auto-detection")
        
        # Auto-detection: prefer OpenAI for embeddings, OpenRouter for chat
        if self.apikey_openai:
            return "openai"
        elif self.apikey_openrouter:
            return "openrouter"
        else:
            raise ValueError("At least one API key (openrouter or openai) must be provided")
    
    def _get_primary_api_key(self) -> str:
        """Get API key for the primary provider."""
        if self.primary_provider == "openai":
            return self.apikey_openai
        elif self.primary_provider == "openrouter":
            return self.apikey_openrouter
        else:
            raise ValueError(f"Unknown primary provider: {self.primary_provider}")
    
    def get_provider_for_task(self, task: str = "chat") -> str:
        """
        Get the best provider for a specific task.
        
        Args:
            task: Task type ("chat", "embedding", "completion")
            
        Returns:
            Provider name for the task
        """
        # For embeddings, always prefer OpenAI if available
        if task == "embedding" and "openai" in self.clients:
            return "openai"
        
        # For other tasks, use primary provider or preferred
        return self.primary_provider
    