"""
Provider manager for LLM client.

Manages initialization and access to LLM provider clients.
"""

import logging
from typing import Any, Dict, Optional

from openai import OpenAI

from .config_builder import ConfigBuilder

logger = logging.getLogger(__name__)


class ProviderManager:
    """Manages LLM provider clients and API keys."""

    def __init__(
        self,
        apikey_openrouter: Optional[str] = None,
        apikey_openai: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        django_config: Optional[Any] = None
    ):
        """
        Initialize provider manager.

        Args:
            apikey_openrouter: OpenRouter API key
            apikey_openai: OpenAI API key
            preferred_provider: Preferred provider ("openai" or "openrouter")
            django_config: Django configuration object
        """
        self.apikey_openrouter = apikey_openrouter
        self.apikey_openai = apikey_openai
        self.preferred_provider = preferred_provider
        self.django_config = django_config

        # Initialize clients dictionary
        self.clients: Dict[str, OpenAI] = {}

        # Initialize clients for available providers
        self._init_openrouter_client()
        self._init_openai_client()

        # Determine primary provider
        self.primary_provider = self._determine_primary_provider()

        # Get primary client
        self.primary_client = self.clients[self.primary_provider]

        logger.info(f"Initialized ProviderManager with primary provider: {self.primary_provider}")

    def _init_openrouter_client(self):
        """Initialize OpenRouter client if API key is available."""
        if self.apikey_openrouter:
            try:
                headers = ConfigBuilder.get_openrouter_headers(self.django_config)
                self.clients["openrouter"] = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.apikey_openrouter,
                    default_headers=headers
                )
                logger.info("OpenRouter client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenRouter client: {e}")

    def _init_openai_client(self):
        """Initialize OpenAI client if API key is available."""
        if self.apikey_openai:
            try:
                self.clients["openai"] = OpenAI(api_key=self.apikey_openai)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    def _determine_primary_provider(self) -> str:
        """
        Determine primary provider based on preference and available keys.

        Returns:
            Primary provider name

        Raises:
            ValueError: If no provider is available
        """
        # If preferred provider is explicitly set and available, use it
        if self.preferred_provider:
            if self.preferred_provider == "openai" and "openai" in self.clients:
                return "openai"
            elif self.preferred_provider == "openrouter" and "openrouter" in self.clients:
                return "openrouter"
            else:
                logger.warning(
                    f"Preferred provider '{self.preferred_provider}' not available, "
                    f"falling back to auto-detection"
                )

        # Auto-detection: prefer OpenAI for better compatibility
        if "openai" in self.clients:
            return "openai"
        elif "openrouter" in self.clients:
            return "openrouter"
        else:
            raise ValueError(
                "At least one API key (openrouter or openai) must be provided"
            )

    def get_client(self, provider: Optional[str] = None) -> OpenAI:
        """
        Get client for specific provider or primary.

        Args:
            provider: Provider name (None for primary)

        Returns:
            OpenAI client instance

        Raises:
            ValueError: If provider is not available
        """
        if provider:
            if provider not in self.clients:
                raise ValueError(f"Provider '{provider}' not available")
            return self.clients[provider]
        return self.primary_client

    def has_provider(self, provider: str) -> bool:
        """
        Check if provider is available.

        Args:
            provider: Provider name

        Returns:
            True if provider is available
        """
        return provider in self.clients

    def get_available_providers(self) -> list:
        """
        Get list of available providers.

        Returns:
            List of provider names
        """
        return list(self.clients.keys())
