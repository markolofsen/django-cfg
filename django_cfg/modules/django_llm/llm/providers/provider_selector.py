"""
Provider selector for LLM client.

Selects optimal provider for specific tasks.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .provider_manager import ProviderManager

logger = logging.getLogger(__name__)


class ProviderSelector:
    """Selects optimal provider for specific tasks."""

    def __init__(self, provider_manager: 'ProviderManager'):
        """
        Initialize provider selector.

        Args:
            provider_manager: ProviderManager instance
        """
        self.provider_manager = provider_manager

    def get_provider_for_task(self, task: str = "chat") -> str:
        """
        Get the best provider for a specific task.

        Args:
            task: Task type ("chat", "embedding", "completion")

        Returns:
            Provider name for the task
        """
        # For embeddings, always prefer OpenAI if available
        # OpenRouter doesn't have proper embedding support
        if task == "embedding" and self.provider_manager.has_provider("openai"):
            logger.debug("Selecting OpenAI for embedding task")
            return "openai"

        # For other tasks, use primary provider
        provider = self.provider_manager.primary_provider
        logger.debug(f"Selecting {provider} for {task} task")
        return provider

    def should_use_mock_embedding(self, provider: str) -> bool:
        """
        Determine if mock embedding should be used for provider.

        Args:
            provider: Provider name

        Returns:
            True if mock embedding should be used
        """
        # OpenRouter doesn't support real embeddings
        return provider == "openrouter"
