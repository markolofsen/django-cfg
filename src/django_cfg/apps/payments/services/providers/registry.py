"""
Provider registry for managing payment providers.

Central registry with lazy loading and typed configuration.
"""

import logging
from typing import Optional, List

from .base import PaymentProvider
from .nowpayments import NowPaymentsProvider, NowPaymentsConfig
from .cryptapi import CryptAPIProvider, CryptAPIConfig
from .cryptomus import CryptomusProvider, CryptomusConfig

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Central registry for payment providers with typed configs."""
    
    def __init__(self):
        """Initialize registry with lazy loading."""
        self._providers: dict[str, PaymentProvider] = {}
        self._provider_configs: dict[str, dict] = {}
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        """Load provider configurations."""
        try:
            from ...utils.config_utils import get_payments_config
            config = get_payments_config()
            
            self._provider_configs = {}
            for provider_name, provider_config in config.providers.items():
                if provider_config.enabled:
                    self._provider_configs[provider_name] = provider_config.get_config_dict()
                    
        except Exception as e:
            logger.warning(f"Failed to load provider configurations: {e}")
            self._provider_configs = {}
    
    def _create_provider(self, name: str, config_dict: dict) -> Optional[PaymentProvider]:
        """Create provider instance from configuration with typed config."""
        try:
            if name == 'nowpayments':
                config = NowPaymentsConfig(**config_dict)
                return NowPaymentsProvider(config)
            elif name == 'cryptapi':
                config = CryptAPIConfig(**config_dict)
                return CryptAPIProvider(config)
            elif name == 'cryptomus':
                config = CryptomusConfig(**config_dict)
                return CryptomusProvider(config)
            elif name == 'stripe':
                # TODO: Implement StripeProvider with StripeConfig
                return None
            else:
                logger.warning(f"Unknown provider type: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create provider {name}: {e}")
            return None
    
    def register_provider(self, name: str, provider: PaymentProvider) -> None:
        """Register a payment provider instance."""
        self._providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[PaymentProvider]:
        """Get provider by name with lazy loading."""
        # Check if already loaded
        if name in self._providers:
            return self._providers[name]
        
        # Try to load from configuration
        if name in self._provider_configs:
            provider = self._create_provider(name, self._provider_configs[name])
            if provider:
                self._providers[name] = provider
                return provider
        
        return None
    
    def list_providers(self) -> List[str]:
        """Get list of available providers."""
        available = set(self._providers.keys())
        available.update(self._provider_configs.keys())
        return list(available)
    
    def get_active_providers(self) -> List[str]:
        """Get list of active providers."""
        active = []
        for name in self.list_providers():
            provider = self.get_provider(name)
            if provider and provider.is_enabled():
                active.append(name)
        return active
    
    def reload_providers(self) -> None:
        """Reload all providers from configuration."""
        logger.info("Reloading providers from configuration")
        self._providers.clear()
        self._load_configurations()
