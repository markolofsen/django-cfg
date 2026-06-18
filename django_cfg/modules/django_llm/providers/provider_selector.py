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
        # Route every task — including embeddings — through the primary
        # provider. The old policy hard-pinned embeddings to OpenAI when
        # an OpenAI key was present, which surfaced as a hard outage the
        # moment the OpenAI account's quota was exhausted (429); OpenRouter
        # serves embeddings via its OpenAI-compatible /embeddings endpoint
        # and is happy to carry the load.
        #
        # A deployment that wants the direct-OpenAI hop for latency sets
        # its primary provider to OpenAI on its side — that's the explicit
        # knob; we don't override it here for one task family.
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
