"""
Cost calculation utilities for LLM services.

Provides accurate cost calculation using models cache and fallback pricing.
"""

import logging
from typing import Dict, Optional

from .models import ModelsCache

logger = logging.getLogger(__name__)


class CostCalculator:
    """Calculate costs for LLM operations using models cache and fallback pricing."""

    def __init__(self, models_cache: Optional[ModelsCache] = None):
        """
        Initialize cost calculator.

        Args:
            models_cache: ModelsCache instance for dynamic pricing

        There are NO hardcoded price maps here any more. The catalogue
        (``ModelsCache``, fed from OpenRouter's chat AND embeddings
        endpoints) is the single source of truth; on a cache miss the
        estimators return ``0.0`` + a warning rather than a stale static
        price. This is a client-side ESTIMATE path — the cost-of-record is
        computed by the gateway's ``cost.calculate_cost`` against the DB.
        """
        self.models_cache = models_cache

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
                    logger.debug(f"Model {model} not found in models cache")
            except Exception as e:
                logger.warning(f"Failed to calculate chat cost from models cache: {e}")

        # No static fallback: the catalogue is the single source of truth.
        # An unknown model yields a 0.0 estimate + warning (this is a
        # client-side estimate, not the cost-of-record billed by the gateway).
        logger.warning(f"No catalogue price for chat model {model!r}; returning 0.0 estimate")
        return 0.0

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
                    logger.debug(f"Embedding model {model} not found in models cache")
            except Exception as e:
                logger.warning(f"Failed to calculate embedding cost from models cache: {e}")

        # No static fallback: embedding prices now come from the catalogue
        # (OpenRouter `/embeddings/models`). Unknown model → 0.0 estimate +
        # warning (client-side estimate, not the gateway cost-of-record).
        logger.warning(f"No catalogue price for embedding model {model!r}; returning 0.0 estimate")
        return 0.0

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
                    logger.debug(f"Model {model} not found in models cache for cost estimation")
            except Exception as e:
                logger.warning(f"Failed to estimate cost from models cache: {e}")

        # No static fallback: unknown model → 0.0 estimate + warning.
        logger.warning(f"No catalogue price for model {model!r} estimate; returning 0.0")
        return 0.0


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
