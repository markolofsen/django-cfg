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
        # For embeddings, prefer a direct OpenAI key when present (lowest
        # latency, no routing hop). Otherwise OpenRouter serves embeddings
        # via its OpenAI-compatible /embeddings endpoint — a REAL call, not
        # a mock. The project's canonical embedding models
        # (openai/text-embedding-3-*) are OpenRouter slugs and both the
        # OpenAI and OpenRouter embedders handle the prefix correctly.
        if task == "embedding" and self.provider_manager.has_provider("openai"):
            logger.debug("Selecting OpenAI for embedding task")
            return "openai"

        # For other tasks, use primary provider
        provider = self.provider_manager.primary_provider
        logger.debug(f"Selecting {provider} for {task} task")
        return provider

    def should_use_mock_embedding(self, provider: str) -> bool:
        """
        Whether to fall back to the MD5 mock embedder.

        Mock is now a LAST RESORT only — both OpenAI and OpenRouter have
        real embedding paths (OpenRouter via its OpenAI-compatible
        endpoint). Returns True only when the resolved provider has no
        usable client (e.g. no API key configured at all).

        Args:
            provider: Provider name

        Returns:
            True if mock embedding should be used
        """
        return not self.provider_manager.has_provider(provider)
