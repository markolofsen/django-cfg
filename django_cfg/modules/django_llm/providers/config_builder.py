"""
Configuration builder for LLM providers.

Builds provider-specific configurations and headers.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


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
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "headers": ConfigBuilder.get_openrouter_headers(django_config)
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "headers": {}
            }
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
            "openai": "gpt-4o-mini"
        }
        return default_models.get(provider, "gpt-4o-mini")
