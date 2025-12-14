"""
OpenAI provider for API key validation.

OpenAI does not provide a balance check API, so this provider validates
the API key by making a test request (list models) and detects:
- Invalid API key (401)
- Insufficient funds (429, quota exceeded errors)
- Other API issues
"""

from openai import OpenAI, AuthenticationError, RateLimitError, APIError

from django_cfg.core.config import get_current_config

from .base import BaseLLMProvider
from ..models import BalanceResponse


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API key validator.

    NOTE: OpenAI does not provide an API to check credit balance.
    This provider validates the API key by making a test request.

    Detects:
    - ✅ API key valid and working
    - ❌ Invalid API key (401)
    - ❌ Insufficient funds (quota exceeded)
    - ❌ Other API errors

    Balance must be checked manually at:
    https://platform.openai.com/settings/organization/billing/overview
    """

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openai"

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

        api_key = config.api_keys.openai
        if not api_key:
            raise ValueError("OpenAI API key not configured")

        # Handle Pydantic SecretStr
        if hasattr(api_key, 'get_secret_value'):
            return api_key.get_secret_value()
        return str(api_key)

    def _fetch_balance(self) -> BalanceResponse:
        """
        Validate OpenAI API key by making test request.

        Returns:
            BalanceResponse with validation result

        Note:
            Balance cannot be checked via API - manual check required at:
            https://platform.openai.com/settings/organization/billing/overview
        """
        api_key = self._get_api_key()

        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Make test request - list models (lightweight operation)
            models = client.models.list()

            # If we got here, API key is valid
            return BalanceResponse(
                balance=None,  # Balance not available via API
                currency="usd",
                status="valid",
                note="Balance check not available via API. Check manually at: "
                     "https://platform.openai.com/settings/organization/billing/overview"
            )

        except AuthenticationError as e:
            # Invalid API key
            return BalanceResponse(
                balance=0.0,
                currency="usd",
                error=f"Invalid API key: {str(e)}",
                note="Check API key at: https://platform.openai.com/account/api-keys"
            )

        except RateLimitError as e:
            # Rate limit or quota exceeded (often means insufficient funds)
            error_msg = str(e)
            if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                return BalanceResponse(
                    balance=0.0,
                    currency="usd",
                    error=f"Insufficient funds or quota exceeded: {error_msg}",
                    note="Add funds at: https://platform.openai.com/account/billing/overview"
                )
            else:
                return BalanceResponse(
                    balance=0.0,
                    currency="usd",
                    error=f"Rate limit exceeded: {error_msg}",
                    note="Try again later or upgrade plan"
                )

        except APIError as e:
            # Generic API error
            return BalanceResponse(
                balance=0.0,
                currency="usd",
                error=f"OpenAI API error: {str(e)}",
                note="Check OpenAI status: https://status.openai.com"
            )
