"""
Models query API for LLM client.

Provides simplified interface to query models cache.
"""

import logging
from typing import Any, Dict, List, Optional

from ..models_cache import ModelInfo, ModelsCache

logger = logging.getLogger(__name__)


class ModelsQueryAPI:
    """Provides query interface to models cache."""

    def __init__(self, models_cache: Optional[ModelsCache] = None):
        """
        Initialize models query API.

        Args:
            models_cache: Optional models cache instance
        """
        self.models_cache = models_cache

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
        """
        Get information about a specific model.

        Args:
            model_id: Model identifier

        Returns:
            ModelInfo or None if not found
        """
        if not self.models_cache:
            return None

        return self.models_cache.get_model(model_id)

    def get_models_by_price(
        self,
        min_price: float = 0.0,
        max_price: float = float('inf')
    ) -> List[ModelInfo]:
        """
        Get models within a price range.

        Args:
            min_price: Minimum price
            max_price: Maximum price

        Returns:
            List of ModelInfo objects
        """
        if not self.models_cache:
            return []

        return self.models_cache.get_models_by_price_range(min_price, max_price)

    def get_free_models(self) -> List[ModelInfo]:
        """
        Get all free models.

        Returns:
            List of free ModelInfo objects
        """
        if not self.models_cache:
            return []

        return self.models_cache.get_free_models()

    def get_budget_models(self, max_price: float = 1.0) -> List[ModelInfo]:
        """
        Get budget-friendly models.

        Args:
            max_price: Maximum price threshold

        Returns:
            List of budget ModelInfo objects
        """
        if not self.models_cache:
            return []

        return self.models_cache.get_budget_models(max_price)

    def get_premium_models(self, min_price: float = 10.0) -> List[ModelInfo]:
        """
        Get premium models.

        Args:
            min_price: Minimum price threshold

        Returns:
            List of premium ModelInfo objects
        """
        if not self.models_cache:
            return []

        return self.models_cache.get_premium_models(min_price)

    def search_models(self, query: str) -> List[ModelInfo]:
        """
        Search models by name, description, or tags.

        Args:
            query: Search query string

        Returns:
            List of matching ModelInfo objects
        """
        if not self.models_cache:
            return []

        return self.models_cache.search_models(query)

    def get_models_summary(self) -> Dict[str, Any]:
        """
        Get summary of available models.

        Returns:
            Dictionary with models summary statistics
        """
        if not self.models_cache:
            return {"error": "Models cache not available for this provider"}

        return self.models_cache.get_models_summary()

    def get_models_cache_info(self) -> Dict[str, Any]:
        """
        Get models cache information.

        Returns:
            Dictionary with cache information
        """
        if not self.models_cache:
            return {"error": "Models cache not available for this provider"}

        return self.models_cache.get_cache_info()

    def clear_models_cache(self):
        """Clear the models cache."""
        if self.models_cache:
            self.models_cache.clear_cache()
            logger.info("Models cache cleared")
