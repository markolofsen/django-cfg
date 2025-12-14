"""
OpenRouter provider for balance checking.

Uses OpenRouter REST API to fetch key info and usage stats.
"""

import httpx

from django_cfg.core.config import get_current_config

from .base import BaseLLMProvider
from ..models import BalanceResponse


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter balance provider using REST API.

    Endpoint: GET https://openrouter.ai/api/v1/credits
    Returns total credits purchased and used (prepaid balance).
    """

    # OpenRouter Credits API
    API_URL = "https://openrouter.ai/api/v1/credits"

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openrouter"

    def _get_api_key(self) -> str:
        """
        Get API key from Django config.

        Returns:
            API key string

        Raises:
            ValueError: If API key not configured
        """
        config = get_current_config()
        if not config or not hasattr(config, 'api_keys') or not config.api_keys:
            raise ValueError("Config not available")

        api_key = config.api_keys.openrouter
        if not api_key:
            raise ValueError("OpenRouter API key not configured")

        # Handle Pydantic SecretStr
        if hasattr(api_key, 'get_secret_value'):
            return api_key.get_secret_value()
        return str(api_key)

    def _fetch_balance(self) -> BalanceResponse:
        """
        Fetch OpenRouter balance via REST API.

        Returns:
            BalanceResponse with balance data

        Raises:
            httpx.HTTPStatusError: On API errors
            ValueError: If API key not configured
        """
        import logging
        logger = logging.getLogger(__name__)

        api_key = self._get_api_key()

        # Log API key length for debugging (не показываем сам ключ)
        logger.debug(f"OpenRouter API key length: {len(api_key)}")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    self.API_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                # Log response for debugging
                logger.debug(f"OpenRouter response status: {response.status_code}")

                if response.status_code == 401:
                    # Invalid API key
                    return BalanceResponse(
                        balance=0.0,
                        currency="usd",
                        error="Invalid OpenRouter API key (401 Unauthorized)",
                        note="Check API key at: https://openrouter.ai/keys"
                    )

                response.raise_for_status()
                data = response.json()

                # Log full response for debugging
                logger.debug(f"OpenRouter API full response: {data}")

                # OpenRouter /api/v1/credits returns:
                # {
                #   "data": {
                #     "total_credits": 10.0,  # Total prepaid credits purchased
                #     "total_usage": 8.5      # Total usage in USD
                #   }
                # }
                credit_data = data.get("data", {})
                total_credits = credit_data.get("total_credits", 0.0)
                total_usage = credit_data.get("total_usage", 0.0)

                # Balance = credits - usage
                balance = total_credits - total_usage

                return BalanceResponse(
                    balance=round(balance, 2),
                    usage=round(total_usage, 2),
                    limit=round(total_credits, 2),
                    currency="usd",
                )

        except httpx.HTTPStatusError as e:
            # HTTP error
            error_msg = f"OpenRouter API error ({e.response.status_code})"
            return BalanceResponse(
                balance=0.0,
                currency="usd",
                error=error_msg,
                note="Check https://openrouter.ai/keys"
            )
