"""
Configuration builder for LLM providers.

Builds provider-specific configurations and headers.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


PROVIDER_BASE_URLS: Dict[str, str] = {
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
    "gonkagate": "https://api.gonkagate.com/v1",
}
"""Provider -> OpenAI-compatible base URL. The single source of truth.

``ProviderManager`` builds its clients from this, ``get_provider_config`` returns
it, and callers outside this module (the CRM chat agent needs a base URL to hand
pydantic-ai) read it rather than hardcoding a URL of their own. The string was
previously repeated in both places here plus every consumer.

A provider absent from this map has no OpenAI-compatible endpoint and cannot be
served by ``OpenAI(base_url=...)``.
"""


class ConfigBuilder:
    """Builds configuration for LLM providers."""

    @staticmethod
    def get_openrouter_headers(django_config: Optional[Any] = None) -> Dict[str, str]:
        """
        Build headers for OpenRouter API.

        Args:
            django_config: Django configuration object

        Returns:
            Dictionary of headers for OpenRouter
        """
        headers = {}

        if django_config:
            try:
                site_url = getattr(django_config, 'site_url', 'http://localhost:8000')
                project_name = getattr(django_config, 'project_name', 'Django CFG')
                headers.update({
                    "HTTP-Referer": site_url,
                    "X-Title": project_name
                })
            except Exception as e:
                logger.warning(f"Failed to extract config for OpenRouter headers: {e}")

        return headers

    @staticmethod
    def get_provider_config(
        provider: str,
        django_config: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Get full provider configuration.

        Args:
            provider: Provider name ("openai" or "openrouter")
            django_config: Django configuration object

        Returns:
            Provider configuration dictionary

        Raises:
            ValueError: If provider is not supported
        """
        base_configs = {
            name: {
                "base_url": url,
                "headers": (
                    ConfigBuilder.get_openrouter_headers(django_config)
                    if name == "openrouter"
                    else {}
                ),
            }
            for name, url in PROVIDER_BASE_URLS.items()
        }

        if provider not in base_configs:
            raise ValueError(f"Unsupported provider: {provider}")

        config = base_configs[provider].copy()

        # Add custom headers from LLM config if available
        if django_config:
            try:
                if hasattr(django_config, 'llm') and django_config.llm:
                    llm_config = django_config.llm
                    if hasattr(llm_config, 'custom_headers'):
                        config["headers"].update(llm_config.custom_headers)
            except Exception as e:
                logger.warning(f"Failed to add custom headers: {e}")

        return config

    @staticmethod
    def get_default_model(provider: str) -> str:
        """
        Get default model for provider.

        Args:
            provider: Provider name

        Returns:
            Default model ID
        """
        default_models = {
            "openrouter": "openai/gpt-4o-mini",
            "openai": "gpt-4o-mini",
            "gonkagate": "moonshotai/kimi-k2.6"
        }
        return default_models.get(provider, "gpt-4o-mini")
