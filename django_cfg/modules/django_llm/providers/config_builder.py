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
    # The sdkrouter edge proxy. Speaks OpenAI-compatible `/v1`, holds every
    # provider credential as a Cloudflare Worker secret, and accepts one token
    # that is useless anywhere else — a leaked token buys an attacker the
    # proxy, not the upstream balance.
    #
    # Replaced `gonkagate` (`api.gonkagate.com`, on Railway) on 2026-09-02.
    "sdkrouter": "https://llm.sdkrouter.com/v1",
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
    def get_openrouter_headers(config: Optional[Any] = None) -> Dict[str, str]:
        """
        Build headers for OpenRouter API.

        Args:
            config: Optional host configuration object.

        Returns:
            Dictionary of headers for OpenRouter
        """
        headers = {}

        if config:
            try:
                site_url = getattr(config, "site_url", "http://localhost:8000")
                project_name = getattr(config, "project_name", "cmdop-llm")
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
            # A Cloudflare Workers AI alias the proxy resolves — `@cf-fast`
            # currently lands on `cf/openai/gpt-oss-20b`. Verified live
            # 2026-09-02, not guessed; the proxy 404s an alias it does not
            # publish rather than falling through to something else.
            #
            # NOT a bare `gpt-4o-mini`: the proxy answers
            # "holds no credential for 'gpt-4o-mini'" for the unprefixed name
            # and routes `openai/gpt-4o-mini` fine. Prefixes matter here.
            "sdkrouter": "@cf-fast",
        }
        return default_models.get(provider, "gpt-4o-mini")
