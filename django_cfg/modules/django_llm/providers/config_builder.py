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
}
"""Provider -> OpenAI-compatible base URL. The single source of truth.

``ProviderManager`` builds its clients from this, ``get_provider_config`` returns
it, and callers outside this module (the CRM chat agent needs a base URL to hand
pydantic-ai) read it rather than hardcoding a URL of their own. The string was
previously repeated in both places here plus every consumer.

A provider absent from this map has no OpenAI-compatible endpoint and cannot be
served by ``OpenAI(base_url=...)``.
"""


def openrouter_identity(config: Optional[Any] = None) -> tuple[str, str]:
    """``(X-Title, HTTP-Referer)`` OpenRouter shows for this project.

    The title is the deployment's ``project_name`` (the ops identity, which is
    what a bill is read against), the referer its ``site_url``. Without a
    configured project the title is a neutral ``"Project"`` and the referer is
    empty: this package must not announce another product's name or domain.
    """
    if config is None:
        from django_cfg.core.state import get_current_config

        config = get_current_config()
    title = getattr(config, "project_name", "") or "Project"
    return title, getattr(config, "site_url", "") or ""


class ConfigBuilder:
    """Builds configuration for LLM providers."""

    @staticmethod
    def get_openrouter_headers(config: Optional[Any] = None) -> Dict[str, str]:
        """
        Build headers for OpenRouter API.

        Args:
            config: Optional host configuration object.

        Returns:
            Dictionary of headers for OpenRouter
        """
        title, referer = openrouter_identity(config)
        headers = {"X-Title": title}
        if referer:
            headers["HTTP-Referer"] = referer

        return headers

    @staticmethod
    def get_provider_config(
        provider: str,
        config: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Get full provider configuration.

        Args:
            provider: Provider name ("openai" or "openrouter")
            config: Optional host configuration object.

        Returns:
            Provider configuration dictionary

        Raises:
            ValueError: If provider is not supported
        """
        base_configs = {
            name: {
                "base_url": url,
                "headers": (
                    ConfigBuilder.get_openrouter_headers(config)
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
        if config:
            try:
                if hasattr(config, "llm") and config.llm:
                    llm_config = config.llm
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
        }
        return default_models.get(provider, "gpt-4o-mini")
