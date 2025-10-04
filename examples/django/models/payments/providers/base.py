"""
Base provider configuration for payment providers.
"""

from pydantic import BaseModel, Field
from typing import Dict


class BaseProviderConfig(BaseModel):
    """Base configuration for payment providers."""

    provider_name: str = Field(..., description="Provider name")
    enabled: bool = Field(default=True, description="Whether provider is enabled")

    def get_provider_config(self) -> Dict[str, any]:
        """Get provider-specific configuration."""
        return {
            'provider_name': self.provider_name,
            'enabled': self.enabled,
        }


__all__ = [
    "BaseProviderConfig",
]
