"""
LLM Provider Balance Checker.

Orchestrates balance checking across multiple LLM providers.
Uses modular provider classes for extensibility.
"""

import logging
from typing import Dict

from .models import BalanceResponse
from .providers import OpenAIProvider, OpenRouterProvider

logger = logging.getLogger("django_cfg.llm_monitoring")


class BalanceChecker:
    """
    Check LLM provider account balances.

    Uses modular provider architecture for easy extensibility.
    Each provider handles its own API authentication and data fetching.
    """

    def __init__(self):
        """Initialize balance checker with all providers."""
        # Initialize providers (API keys loaded from config on-demand)
        self.providers = {
            "openai": OpenAIProvider(),
            "openrouter": OpenRouterProvider(),
        }

    def check_openai_balance(self, force: bool = False) -> BalanceResponse:
        """
        Check OpenAI account balance.

        NOTE: OpenAI does not provide an API for checking balance.
        This always returns an error response.

        Args:
            force: If True, bypass cache and fetch fresh data

        Returns:
            BalanceResponse with error message

        Example:
            >>> checker = BalanceChecker()
            >>> result = checker.check_openai_balance()
            >>> print(result.error)
        """
        return self.providers["openai"].check_balance(force=force)

    def check_openrouter_balance(self, force: bool = False) -> BalanceResponse:
        """
        Check OpenRouter account balance.

        Args:
            force: If True, bypass cache and fetch fresh data

        Returns:
            BalanceResponse with balance data

        Example:
            >>> checker = BalanceChecker()
            >>> result = checker.check_openrouter_balance()
            >>> print(f"Balance: ${result.balance:.2f}")
        """
        return self.providers["openrouter"].check_balance(force=force)

    def check_all_balances(self, force: bool = False) -> Dict[str, BalanceResponse]:
        """
        Check all LLM provider balances.

        Args:
            force: If True, bypass cache for all checks

        Returns:
            Dict with provider names as keys and BalanceResponse as values

        Example:
            >>> checker = BalanceChecker()
            >>> balances = checker.check_all_balances()
            >>> for provider, data in balances.items():
            ...     if not data.error:
            ...         print(f"{provider}: ${data.balance:.2f}")
        """
        return {
            name: provider.check_balance(force=force)
            for name, provider in self.providers.items()
        }
