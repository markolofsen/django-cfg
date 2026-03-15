"""
Base provider class for LLM balance checking.

All provider implementations should inherit from this base class.
"""

import logging
from abc import ABC, abstractmethod

from django.core.cache import cache

from ..models import BalanceResponse

logger = logging.getLogger("django_cfg.llm_monitoring")


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM balance providers.

    Provides common functionality:
    - Caching (1 hour TTL)
    - Type-safe responses (Pydantic)
    - Error handling

    Subclasses must implement:
    - get_provider_name(): Return provider name (e.g., "openai")
    - _fetch_balance(): Fetch balance from provider API
    """

    # Cache TTL: 1 hour
    CACHE_TTL = 60 * 60

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get provider name for logging and cache keys.

        Returns:
            Provider name (e.g., "openai", "openrouter")
        """
        pass

    @abstractmethod
    def _fetch_balance(self) -> BalanceResponse:
        """
        Fetch balance from provider API.

        Returns:
            BalanceResponse with balance data

        Raises:
            Exception: On API errors
        """
        pass

    def check_balance(self, force: bool = False) -> BalanceResponse:
        """
        Check provider balance with caching.

        Args:
            force: If True, bypass cache and fetch fresh data

        Returns:
            BalanceResponse with balance data or error

        Example:
            >>> provider = OpenRouterProvider()
            >>> result = provider.check_balance()
            >>> print(f"Balance: ${result.balance:.2f}")
        """
        provider_name = self.get_provider_name()
        cache_key = f"llm_monitoring:{provider_name}_balance"

        # Try cache first (unless force=True)
        if not force:
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"{provider_name.title()} balance retrieved from cache")
                # Reconstruct Pydantic model from cached dict
                return BalanceResponse(**cached)

        try:
            logger.info(f"Fetching {provider_name.title()} balance from API")

            # Call provider-specific implementation
            result = self._fetch_balance()

            # Cache result as dict
            cache.set(cache_key, result.model_dump(), self.CACHE_TTL)

            # Log success
            if result.balance is not None:
                logger.info(f"{provider_name.title()} balance: ${result.balance:.2f}")
            elif result.status:
                logger.info(f"{provider_name.title()} API key status: {result.status}")
            else:
                logger.info(f"{provider_name.title()} check complete")

            return result

        except Exception as e:
            error_msg = f"{provider_name.title()} API request failed: {str(e)}"
            logger.exception(error_msg)
            return BalanceResponse(
                balance=0.0,
                currency="usd",
                error=error_msg
            )
