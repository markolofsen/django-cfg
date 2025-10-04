"""
Cost calculation utilities for LLM services.

Provides accurate cost calculation using models cache and fallback pricing.
"""

import logging
from typing import Dict, Any, Optional

from .models_cache import ModelsCache

logger = logging.getLogger(__name__)


class CostCalculator:
    """Calculate costs for LLM operations using models cache and fallback pricing."""
    
    def __init__(self, models_cache: Optional[ModelsCache] = None):
        """
        Initialize cost calculator.
        
        Args:
            models_cache: ModelsCache instance for dynamic pricing
        """
        self.models_cache = models_cache
        
        # Fallback pricing for common models (per 1M tokens)
        self.fallback_chat_prices = {
            "gpt-4o-mini": {"prompt": 0.15, "completion": 0.6},
            "gpt-4o": {"prompt": 5.0, "completion": 15.0},
            "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
            "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
            "claude-3-sonnet": {"prompt": 3.0, "completion": 15.0},
            "claude-3-opus": {"prompt": 15.0, "completion": 75.0}
        }
        
        # Fallback embedding pricing (per 1K tokens)
        self.fallback_embedding_prices = {
            "text-embedding-ada-002": 0.0001 / 1000,
            "text-embedding-3-small": 0.00002 / 1000,
            "text-embedding-3-large": 0.00013 / 1000,
        }
    
    def calculate_chat_cost(self, usage: Dict[str, int], model: str) -> float:
        """
        Calculate cost for chat completion.
        
        Args:
            usage: Usage dict with prompt_tokens, completion_tokens, total_tokens
            model: Model ID
            
        Returns:
            Cost in USD
        """
        # Try models cache first
        if self.models_cache:
            try:
                cost = self.models_cache.calculate_cost_from_usage(model, usage)
                if cost is not None:
                    logger.debug(f"Using models cache pricing for chat {model}: ${cost:.6f}")
                    return cost
                else:
                    logger.debug(f"Model {model} not found in models cache, using fallback pricing")
            except Exception as e:
                logger.warning(f"Failed to calculate chat cost from models cache: {e}")
        
        # Fallback to hardcoded pricing
        return self._calculate_chat_cost_fallback(usage, model)
    
    def calculate_embedding_cost(self, tokens: int, model: str) -> float:
        """
        Calculate cost for embedding generation.
        
        Args:
            tokens: Number of tokens
            model: Model ID
            
        Returns:
            Cost in USD
        """
        # Try models cache first
        if self.models_cache:
            try:
                usage_dict = {
                    'total_tokens': tokens,
                    'prompt_tokens': tokens,  # For embeddings, all tokens are input tokens
                    'completion_tokens': 0
                }
                cost = self.models_cache.calculate_cost_from_usage(model, usage_dict)
                if cost is not None:
                    logger.debug(f"Using models cache pricing for embedding {model}: ${cost:.6f}")
                    return cost
                else:
                    logger.debug(f"Embedding model {model} not found in models cache, using fallback pricing")
            except Exception as e:
                logger.warning(f"Failed to calculate embedding cost from models cache: {e}")
        
        # Fallback to hardcoded pricing
        return self._calculate_embedding_cost_fallback(tokens, model)
    
    def _calculate_chat_cost_fallback(self, usage: Dict[str, int], model: str) -> float:
        """Calculate chat cost using fallback pricing."""
        total_tokens = usage.get('total_tokens', 0)
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        
        # Find matching model cost
        for model_pattern, costs in self.fallback_chat_prices.items():
            if model_pattern in model.lower():
                prompt_cost = (prompt_tokens / 1_000_000) * costs["prompt"]
                completion_cost = (completion_tokens / 1_000_000) * costs["completion"]
                total_cost = prompt_cost + completion_cost
                logger.debug(f"Using fallback chat pricing for {model}: ${total_cost:.6f}")
                return total_cost
        
        # Default cost (using total tokens with average rate)
        default_cost = (total_tokens / 1_000_000) * 0.5
        logger.debug(f"Using default chat pricing for {model}: ${default_cost:.6f}")
        return default_cost
    
    def _calculate_embedding_cost_fallback(self, tokens: int, model: str) -> float:
        """Calculate embedding cost using fallback pricing."""
        price_per_token = self.fallback_embedding_prices.get(model, 0.0001 / 1000)
        cost = tokens * price_per_token
        logger.debug(f"Using fallback embedding pricing for {model}: ${cost:.6f}")
        return cost
    
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
        # Try models cache first
        if self.models_cache:
            try:
                cost = self.models_cache.get_model_cost_estimate(model, input_tokens, output_tokens)
                if cost is not None:
                    logger.debug(f"Using models cache cost estimate for {model}: ${cost:.6f}")
                    return cost
                else:
                    logger.debug(f"Model {model} not found in models cache for cost estimation, using fallback")
            except Exception as e:
                logger.warning(f"Failed to estimate cost from models cache: {e}")
        
        # Fallback to internal calculation
        usage_dict = {
            'total_tokens': input_tokens + output_tokens,
            'prompt_tokens': input_tokens,
            'completion_tokens': output_tokens
        }
        return self._calculate_chat_cost_fallback(usage_dict, model)


# Global cost calculator instance
_cost_calculator = None


def get_cost_calculator(models_cache=None) -> CostCalculator:
    """Get global cost calculator instance."""
    global _cost_calculator
    if _cost_calculator is None or models_cache is not None:
        _cost_calculator = CostCalculator(models_cache)
    return _cost_calculator


def calculate_chat_cost(usage: Dict[str, int], model: str, models_cache=None) -> float:
    """Calculate cost for chat completion."""
    calculator = get_cost_calculator(models_cache)
    return calculator.calculate_chat_cost(usage, model)


def calculate_embedding_cost(tokens: int, model: str, models_cache=None) -> float:
    """Calculate cost for embedding generation."""
    calculator = get_cost_calculator(models_cache)
    return calculator.calculate_embedding_cost(tokens, model)


def estimate_cost(model: str, input_tokens: int, output_tokens: int, models_cache=None) -> float:
    """Estimate cost for a model."""
    calculator = get_cost_calculator(models_cache)
    return calculator.estimate_cost(model, input_tokens, output_tokens)
