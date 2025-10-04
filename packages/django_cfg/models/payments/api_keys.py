"""
API keys configuration for payment providers.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from .providers.base import BaseProviderConfig


class ProviderAPIKeysConfig(BaseModel):
    """
    API keys configuration for payment providers.

    Stores list of provider configurations.
    """

    providers: List[BaseProviderConfig] = Field(
        default_factory=list,
        description="List of provider configurations"
    )

    def add_provider(self, provider_config: BaseProviderConfig):
        """Add a provider configuration."""
        # Remove existing provider with same name
        self.providers = [p for p in self.providers if p.provider_name != provider_config.provider_name]
        self.providers.append(provider_config)

    def get_provider_config(self, provider: str) -> Dict[str, any]:
        """Get provider-specific configuration."""
        provider_lower = provider.lower()

        for provider_config in self.providers:
            if provider_config.provider_name.lower() == provider_lower:
                return provider_config.get_provider_config()

        return {'enabled': False, 'provider_name': provider}

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled providers."""
        enabled = []
        for provider_config in self.providers:
            config = provider_config.get_provider_config()
            if config.get('enabled', False):
                enabled.append(provider_config.provider_name)
        return enabled

    def get_provider_by_name(self, provider_name: str) -> Optional[BaseProviderConfig]:
        """Get provider configuration by name."""
        for provider_config in self.providers:
            if provider_config.provider_name.lower() == provider_name.lower():
                return provider_config
        return None


__all__ = [
    "ProviderAPIKeysConfig",
]
