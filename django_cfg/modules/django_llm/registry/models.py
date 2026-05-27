"""
OpenRouter Models Cache - Fetch and cache available models with pricing
Adapted for django-cfg from unreal_llm
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
from cachetools import TTLCache

logger = logging.getLogger(__name__)

@dataclass
class ModelPricing:
    """Model pricing information"""
    prompt_price: float  # Price per 1M input tokens
    completion_price: float  # Price per 1M output tokens
    currency: str = "USD"
    image_price: float = 0.0  # Price per image (per token, raw OpenRouter unit)

@dataclass
class OpenRouterModel:
    """OpenRouter model information from the /models catalogue"""
    id: str
    name: str
    description: Optional[str]
    context_length: int
    pricing: ModelPricing
    provider: str
    tags: List[str]
    is_available: bool = True
    input_modalities: List[str] = field(default_factory=list)
    output_modalities: List[str] = field(default_factory=list)
    max_completion_tokens: Optional[int] = None
    is_moderated: bool = False

class ModelsCache:
    """Cache for OpenRouter models with pricing information"""

    DEFAULT_TTL = 86400  # 24 hours default
    DEFAULT_CACHE_SIZE = 100
    CACHE_FILENAME = "openrouter_models.json"

    def __init__(self,
                 api_key: Optional[str] = None,
                 cache_dir: Optional[Path] = None,
                 cache_ttl: int = DEFAULT_TTL,
                 max_cache_size: int = DEFAULT_CACHE_SIZE):
        """
        Initialize models cache

        Args:
            api_key: OpenRouter API key — defaults to the central
                     `_integration.get_api_keys()` accessor when omitted.
            cache_dir: Directory for persistent cache files
            cache_ttl: Cache TTL in seconds (default: 24 hours)
            max_cache_size: Maximum cache size
        """
        if not api_key:
            from .._integration import get_api_keys
            api_key = get_api_keys()["openrouter"]
        self.api_key = api_key
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size

        # Determine cache directory using builder
        from ..storage.dirs import get_models_cache_dir
        self.cache_dir = get_models_cache_dir(cache_dir)
        self.cache_file = self.cache_dir / self.CACHE_FILENAME

        # Memory cache
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)
        self.last_fetch_time: Optional[datetime] = None
        self.models: Dict[str, OpenRouterModel] = {}

        # Cache key for models list
        self.models_cache_key = "openrouter_models"

        # Load from file cache on initialization
        self._load_from_file()

    def _load_from_file(self) -> bool:
        """Load models from file cache"""
        try:
            if not self.cache_file.exists():
                return False

            with open(self.cache_file, encoding='utf-8') as f:
                data = json.load(f)

            # Check if cache is still valid
            fetch_time_str = data.get('fetch_time')
            if fetch_time_str:
                fetch_time = datetime.fromisoformat(fetch_time_str)
                if datetime.now() - fetch_time > timedelta(seconds=self.cache_ttl):
                    logger.debug("File cache expired")
                    return False

            # Parse models
            models_data = data.get('models', {})
            self.models = {}

            for model_id, model_data in models_data.items():
                try:
                    pricing = ModelPricing(
                        prompt_price=model_data['pricing']['prompt_price'],
                        completion_price=model_data['pricing']['completion_price'],
                        currency=model_data['pricing']['currency'],
                        image_price=model_data['pricing'].get('image_price', 0.0)
                    )

                    model_info = OpenRouterModel(
                        id=model_data['id'],
                        name=model_data['name'],
                        description=model_data.get('description'),
                        context_length=model_data['context_length'],
                        pricing=pricing,
                        provider=model_data['provider'],
                        tags=model_data.get('tags', []),
                        is_available=model_data.get('is_available', True),
                        input_modalities=model_data.get('input_modalities', []),
                        output_modalities=model_data.get('output_modalities', []),
                        max_completion_tokens=model_data.get('max_completion_tokens'),
                        is_moderated=model_data.get('is_moderated', False)
                    )

                    self.models[model_id] = model_info

                except Exception as e:
                    logger.warning(f"Failed to parse cached model {model_id}: {e}")
                    continue

            if fetch_time_str:
                self.last_fetch_time = datetime.fromisoformat(fetch_time_str)

            # Also update memory cache
            self.cache[self.models_cache_key] = {
                "models": self.models,
                "fetch_time": self.last_fetch_time
            }

            logger.info(f"Loaded {len(self.models)} models from file cache")
            return True

        except Exception as e:
            logger.warning(f"Failed to load models from file cache: {e}")
            return False

    def _save_to_file(self) -> bool:
        """Save models to file cache"""
        try:
            # Prepare data for serialization
            models_data = {}
            for model_id, model_info in self.models.items():
                models_data[model_id] = {
                    'id': model_info.id,
                    'name': model_info.name,
                    'description': model_info.description,
                    'context_length': model_info.context_length,
                    'pricing': {
                        'prompt_price': model_info.pricing.prompt_price,
                        'completion_price': model_info.pricing.completion_price,
                        'currency': model_info.pricing.currency,
                        'image_price': model_info.pricing.image_price
                    },
                    'provider': model_info.provider,
                    'tags': model_info.tags,
                    'is_available': model_info.is_available,
                    'input_modalities': model_info.input_modalities,
                    'output_modalities': model_info.output_modalities,
                    'max_completion_tokens': model_info.max_completion_tokens,
                    'is_moderated': model_info.is_moderated
                }

            data = {
                'models': models_data,
                'fetch_time': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
                'cache_ttl': self.cache_ttl,
                'total_models': len(self.models)
            }

            # Write to file atomically
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            temp_file.replace(self.cache_file)
            logger.debug(f"Saved {len(self.models)} models to file cache")
            return True

        except Exception as e:
            logger.error(f"Failed to save models to file cache: {e}")
            return False

    async def fetch_models(self, force_refresh: bool = False) -> Dict[str, OpenRouterModel]:
        """
        Fetch models from OpenRouter API

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            Dictionary of model_id -> OpenRouterModel
        """
        # Check memory cache first
        if not force_refresh and self.models_cache_key in self.cache:
            logger.debug("Using cached models from memory")
            cached_data = self.cache[self.models_cache_key]
            self.models = cached_data["models"]
            self.last_fetch_time = cached_data["fetch_time"]
            return self.models

        # Check if we have models from file cache and they're still valid
        if not force_refresh and self.models and self.last_fetch_time:
            if datetime.now() - self.last_fetch_time < timedelta(seconds=self.cache_ttl):
                logger.debug("Using models from file cache")
                # Update memory cache
                self.cache[self.models_cache_key] = {
                    "models": self.models,
                    "fetch_time": self.last_fetch_time
                }
                return self.models

        logger.info("Fetching models from OpenRouter API")

        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Parse models
                    self.models = {}
                    for model_data in data.get("data", []):
                        model_info = self._parse_model_data(model_data)
                        if model_info:
                            self.models[model_info.id] = model_info

                    # Update cache
                    self.last_fetch_time = datetime.now()
                    self.cache[self.models_cache_key] = {
                        "models": self.models,
                        "fetch_time": self.last_fetch_time
                    }

                    # Save to file
                    self._save_to_file()

                    logger.info(f"Fetched {len(self.models)} models from OpenRouter")
                    return self.models

        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch models: {e}")
            # Return cached models if available
            if self.models:
                logger.info(f"Using stale cached models ({len(self.models)} models)")
                return self.models
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching models: {e}")
            # Return cached models if available
            if self.models:
                logger.info(f"Using stale cached models ({len(self.models)} models)")
                return self.models
            raise

    def _parse_model_data(self, model_data: Dict[str, Any]) -> Optional[OpenRouterModel]:
        """Parse model data from API response"""
        try:
            # Check required fields
            if not model_data.get("id") or not model_data.get("name"):
                return None

            # Extract pricing information
            pricing_data = model_data.get("pricing", {})
            pricing = ModelPricing(
                prompt_price=pricing_data.get("prompt", 0.0),
                completion_price=pricing_data.get("completion", 0.0),
                currency=pricing_data.get("currency", "USD"),
                image_price=float(pricing_data.get("image", 0.0) or 0.0)
            )

            # Capabilities from architecture / top_provider blocks
            architecture = model_data.get("architecture", {})
            top_provider = model_data.get("top_provider", {})

            # Create model info
            model_info = OpenRouterModel(
                id=model_data.get("id", ""),
                name=model_data.get("name", ""),
                description=model_data.get("description"),
                context_length=model_data.get("context_length", 0),
                pricing=pricing,
                provider=model_data.get("provider", ""),
                tags=model_data.get("tags", []),
                is_available=model_data.get("available", True),
                input_modalities=architecture.get("input_modalities", []),
                output_modalities=architecture.get("output_modalities", []),
                max_completion_tokens=top_provider.get("max_completion_tokens"),
                is_moderated=top_provider.get("is_moderated", False)
            )

            return model_info

        except Exception as e:
            logger.warning(f"Failed to parse model data: {e}")
            return None

    def get_model(self, model_id: str) -> Optional[OpenRouterModel]:
        """Get model information by ID"""
        return self.models.get(model_id)

    def get_models_by_provider(self, provider: str) -> List[OpenRouterModel]:
        """Get all models from a specific provider"""
        return [model for model in self.models.values() if model.provider == provider]

    def get_models_by_price_range(self,
                                 min_price: float = 0.0,
                                 max_price: float = float('inf'),
                                 price_type: str = "prompt") -> List[OpenRouterModel]:
        """
        Get models within a price range
        
        Args:
            min_price: Minimum price per 1M tokens
            max_price: Maximum price per 1M tokens
            price_type: "prompt" or "completion"
            
        Returns:
            List of models in price range
        """
        filtered_models = []

        for model in self.models.values():
            if not model.is_available:
                continue

            price = model.pricing.prompt_price if price_type == "prompt" else model.pricing.completion_price

            if min_price <= price <= max_price:
                filtered_models.append(model)

        # Sort by price
        filtered_models.sort(key=lambda m: m.pricing.prompt_price if price_type == "prompt" else m.pricing.completion_price)

        return filtered_models

    def get_free_models(self) -> List[OpenRouterModel]:
        """Get all free models (price = 0)"""
        return self.get_models_by_price_range(0.0, 0.0)

    def get_budget_models(self, max_price: float = 1.0) -> List[OpenRouterModel]:
        """Get budget models (price <= max_price)"""
        return self.get_models_by_price_range(0.0, max_price)

    def get_premium_models(self, min_price: float = 10.0) -> List[OpenRouterModel]:
        """Get premium models (price >= min_price)"""
        return self.get_models_by_price_range(min_price, float('inf'))

    def search_models(self, query: str) -> List[OpenRouterModel]:
        """Search models by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for model in self.models.values():
            # Search in name
            if query_lower in model.name.lower():
                results.append(model)
                continue

            # Search in description
            if model.description and query_lower in model.description.lower():
                results.append(model)
                continue

            # Search in tags
            if any(query_lower in tag.lower() for tag in model.tags):
                results.append(model)
                continue

        return results

    def get_model_cost_estimate(self,
                               model_id: str,
                               input_tokens: int,
                               output_tokens: int) -> Optional[float]:
        """
        Estimate cost for a model
        
        Args:
            model_id: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        model = self.get_model(model_id)
        if not model:
            return None

        # Calculate cost
        input_cost = (input_tokens / 1_000_000) * model.pricing.prompt_price
        output_cost = (output_tokens / 1_000_000) * model.pricing.completion_price

        return input_cost + output_cost

    def calculate_cost_from_usage(self, model_id: str, usage: Dict[str, int]) -> Optional[float]:
        """
        Calculate cost from OpenAI usage object
        
        Args:
            model_id: Model ID
            usage: Usage dict with prompt_tokens, completion_tokens, total_tokens
            
        Returns:
            Calculated cost in USD
        """
        model = self.get_model(model_id)
        if not model:
            return None

        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)

        # Calculate cost
        input_cost = (prompt_tokens / 1_000_000) * model.pricing.prompt_price
        output_cost = (completion_tokens / 1_000_000) * model.pricing.completion_price

        return input_cost + output_cost

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            "cache_size": len(self.cache),
            "models_count": len(self.models),
            "last_fetch": self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            "cache_ttl": self.cache.ttl,
            "max_cache_size": self.cache.maxsize,
            "cache_file": str(self.cache_file),
            "cache_file_exists": self.cache_file.exists()
        }

    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        self.models.clear()
        self.last_fetch_time = None

        # Also remove file cache
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Removed file cache")
        except Exception as e:
            logger.warning(f"Failed to remove file cache: {e}")

        logger.info("Models cache cleared")

    def get_models_summary(self) -> Dict[str, Any]:
        """Get summary of available models"""
        if not self.models:
            return {"error": "No models loaded"}

        # Count by provider
        provider_counts = {}
        for model in self.models.values():
            provider_counts[model.provider] = provider_counts.get(model.provider, 0) + 1

        # Price ranges
        prices = [model.pricing.prompt_price for model in self.models.values() if model.is_available]

        # Count free models (both prompt and completion prices are 0)
        free_models = [m for m in self.models.values()
                      if m.is_available and m.pricing.prompt_price == 0.0 and m.pricing.completion_price == 0.0]

        return {
            "total_models": len(self.models),
            "available_models": len([m for m in self.models.values() if m.is_available]),
            "providers": provider_counts,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            },
            "free_models_count": len(free_models),
            "budget_models_count": len(self.get_budget_models()),
            "premium_models_count": len(self.get_premium_models()),
            "last_updated": self.last_fetch_time.isoformat() if self.last_fetch_time else None
        }

# Example usage
async def example_models_cache():
    """Example usage of ModelsCache"""
    import os

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Please set OPENROUTER_API_KEY environment variable")
        return

    # Initialize cache
    cache = ModelsCache(api_key=api_key, cache_ttl=86400)  # 24 hours

    try:
        # Fetch models
        models = await cache.fetch_models()
        print(f"Fetched {len(models)} models")

        # Get summary
        summary = cache.get_models_summary()
        print(f"Summary: {summary}")

        # Get free models
        free_models = cache.get_free_models()
        print(f"Free models: {len(free_models)}")
        for model in free_models[:5]:  # Show first 5
            print(f"  - {model.name} ({model.provider})")

        # Get budget models
        budget_models = cache.get_budget_models(max_price=0.5)
        print(f"Budget models (≤$0.5/1M tokens): {len(budget_models)}")

        # Search for coding models
        coding_models = cache.search_models("code")
        print(f"Coding models: {len(coding_models)}")
        for model in coding_models[:3]:
            print(f"  - {model.name}: ${model.pricing.prompt_price}/1M tokens")

        # Estimate cost
        model_id = "openai/gpt-4o-mini"
        cost = cache.get_model_cost_estimate(model_id, 1000, 500)
        print(f"Cost for {model_id} (1000 input + 500 output tokens): ${cost:.6f}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(example_models_cache())
