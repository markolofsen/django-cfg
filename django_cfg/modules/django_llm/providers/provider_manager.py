"""
Provider manager for LLM client.

Manages initialization and access to LLM provider clients.
"""

import itertools
import logging
import threading
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from openai import OpenAI

from .config_builder import PROVIDER_BASE_URLS, ConfigBuilder

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    GONKA = "gonkagate"


# Type alias for provider selection
LLMProviderType = Union[LLMProvider, Literal["openai", "openrouter", "gonkagate"]]


class ProviderManager:
    """Manages LLM provider clients and API keys."""

    def __init__(
        self,
        apikey_openrouter: Optional[str] = None,
        apikey_openai: Optional[str] = None,
        apikey_gonka: Optional[str] = None,
        preferred_provider: Optional[LLMProviderType] = None,
        config: Optional[Any] = None
    ):
        """
        Initialize provider manager.

        Args:
            apikey_openrouter: OpenRouter API key
            apikey_openai: OpenAI API key
            apikey_gonka: gonka (gonkagate) API key
            preferred_provider: Preferred provider ("openai", "openrouter", "gonkagate")
            config: Optional host configuration object.
        """
        self.apikey_openrouter = apikey_openrouter
        self.apikey_openai = apikey_openai
        self.apikey_gonka = apikey_gonka
        # Normalize preferred_provider to string
        if isinstance(preferred_provider, LLMProvider):
            self.preferred_provider = preferred_provider.value
        else:
            self.preferred_provider = preferred_provider
        self.config = config

        # Initialize clients dictionary
        self.clients: Dict[str, OpenAI] = {}

        # Initialize clients for available providers
        self._init_openrouter_client()
        self._init_openai_client()
        self._init_gonka_client()

        # Determine primary provider
        self.primary_provider = self._determine_primary_provider()

        # Get primary client
        self.primary_client = self.clients[self.primary_provider]

        logger.info(f"Initialized ProviderManager with primary provider: {self.primary_provider}")

    def _init_openrouter_client(self):
        """Initialize OpenRouter client if API key is available."""
        if self.apikey_openrouter:
            try:
                headers = ConfigBuilder.get_openrouter_headers(self.config)
                self.clients["openrouter"] = OpenAI(
                    base_url=PROVIDER_BASE_URLS["openrouter"],
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

    def _init_gonka_client(self):
        """Initialize gonka (gonkagate) client(s) if API key(s) available.

        gonka is OpenAI-compatible — same SDK, just a different base_url. It
        serves the gonka network's chat models (e.g. ``minimaxai/minimax-m2.7``,
        ``moonshotai/kimi-k2.6``). No embeddings API.

        ``apikey_gonka`` may be a single key OR a POOL (list). With a pool,
        ``get_client('gonkagate')`` round-robins across one OpenAI client per
        key, so concurrent race legs each ride a different key — sidestepping
        gonka's per-key rate limit (50 concurrent / 600 RPM) and its
        near-identical-burst guard.
        """
        keys = self.apikey_gonka
        if isinstance(keys, str):
            keys = [keys]
        keys = [k for k in (keys or []) if k]
        if not keys:
            return
        try:
            self._gonka_pool: List[OpenAI] = [
                OpenAI(base_url=PROVIDER_BASE_URLS["gonkagate"], api_key=k)
                for k in keys
            ]
            self._gonka_cycle = itertools.cycle(range(len(self._gonka_pool)))
            self._gonka_lock = threading.Lock()
            # Expose the first as the named client (has_provider / primary detection).
            self.clients["gonkagate"] = self._gonka_pool[0]
            logger.info("Gonka (gonkagate) client initialized (pool size=%d)", len(self._gonka_pool))
        except Exception as e:
            logger.error(f"Failed to initialize gonka client: {e}")

    def _next_gonka_client(self) -> OpenAI:
        """Round-robin the gonka key pool (thread-safe)."""
        pool = getattr(self, "_gonka_pool", None)
        if not pool:
            return self.clients["gonkagate"]
        with self._gonka_lock:
            idx = next(self._gonka_cycle)
        return pool[idx]

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
            if self.preferred_provider in self.clients:
                return self.preferred_provider
            else:
                logger.warning(
                    f"Preferred provider '{self.preferred_provider}' not available, "
                    f"falling back to auto-detection"
                )

        # Auto-detection: prefer OpenRouter — wider model catalog
        # (Anthropic, Google, Mistral, open models, image-edit SKUs)
        # and the project-canonical model IDs are OpenRouter-style.
        # Callers that need OpenAI specifically pass
        # ``preferred_provider="openai"`` or call
        # ``LLMClient.activate_provider("openai")``.
        if "openrouter" in self.clients:
            return "openrouter"
        elif "openai" in self.clients:
            return "openai"
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
        name = provider or self.primary_provider
        # gonka: round-robin the key pool so concurrent race legs use distinct keys.
        if name == "gonkagate" and getattr(self, "_gonka_pool", None):
            return self._next_gonka_client()
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
