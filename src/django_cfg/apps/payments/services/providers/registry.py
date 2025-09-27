"""
Provider registry for the Universal Payment System v2.0.

Centralized management of payment providers with health monitoring and fallbacks.
"""

from enum import Enum
from typing import Dict, List, Optional, Type, Any
from django_cfg.modules.django_logger import get_logger
# ConfigService removed - using direct Constance access
from ..types import ServiceOperationResult
from .base import BaseProvider, ProviderConfig
from .nowpayments import NowPaymentsProvider, NowPaymentsConfig

logger = get_logger("provider_registry")


# Provider enums
class ProviderEnum(Enum):
    NOWPAYMENTS = "nowpayments"
    CRYPTAPI = "cryptapi"
    STRIPE = "stripe"
    CRYPTOMUS = "cryptomus"

    @classmethod
    def get_crypto_providers(cls):
        """Get list of crypto provider values."""
        return [cls.NOWPAYMENTS.value, cls.CRYPTAPI.value, cls.CRYPTOMUS.value]
    
    @classmethod
    def get_fiat_providers(cls):
        """Get list of fiat provider values."""
        return [cls.STRIPE.value]

    @classmethod
    def get_priority_order(cls):
        """Get list of provider values in priority order."""
        return [
            cls.NOWPAYMENTS.value, 
            cls.CRYPTAPI.value, 
            cls.STRIPE.value, 
            cls.CRYPTOMUS.value
        ]

class ProviderRegistry:
    """
    Registry for managing payment providers.
    
    Provides centralized access to providers with health monitoring,
    configuration management, and fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize provider registry."""
        # Use PaymentConfigService for configuration
        from ...config.constance import get_payment_config_service

        self.config_service = get_payment_config_service()
        self._providers: Dict[str, BaseProvider] = {}

        self._provider_classes: Dict[str, Type[BaseProvider]] = {
            ProviderEnum.NOWPAYMENTS.value: NowPaymentsProvider,
        }
        self._provider_configs: Dict[str, Type[ProviderConfig]] = {
            ProviderEnum.NOWPAYMENTS.value: NowPaymentsConfig,
        }
        
        self._health_status: Dict[str, bool] = {}
        self._initialized = False
    
    def initialize(self) -> ServiceOperationResult:
        """
        Initialize all configured providers.
        
        Returns:
            ServiceOperationResult: Initialization result
        """
        try:
            logger.info("Initializing provider registry")
            
            # Get all provider configurations
            try:
                provider_configs = self.config_service.get_all_provider_configs()
            except Exception as e:
                return ServiceOperationResult(
                    success=False,
                    message=f"Failed to get provider configurations: {e}",
                    error_code="config_failed"
                )
            
            # provider_configs is already a dict from get_all_provider_configs()
            initialized_count = 0
            failed_providers = []
            
            # Initialize each configured provider
            for provider_name, config_data in provider_configs.items():
                if not config_data.get('enabled', False):
                    logger.debug(f"Skipping disabled provider: {provider_name}")
                    continue
                
                try:
                    provider = self._create_provider(provider_name, config_data)
                    if provider:
                        self._providers[provider_name] = provider
                        initialized_count += 1
                        logger.info(f"Initialized provider: {provider_name}")
                    else:
                        failed_providers.append(provider_name)
                        
                except Exception as e:
                    logger.error(f"Failed to initialize provider {provider_name}: {e}")
                    failed_providers.append(provider_name)
            
            self._initialized = True
            
            # Perform initial health check
            self.health_check_all()
            
            result_message = f"Initialized {initialized_count} providers"
            if failed_providers:
                result_message += f", failed: {', '.join(failed_providers)}"
            
            return ServiceOperationResult(
                success=True,
                message=result_message,
                data={
                    'initialized_providers': list(self._providers.keys()),
                    'failed_providers': failed_providers,
                    'total_configured': len(provider_configs),
                    'initialized_count': initialized_count
                }
            )
            
        except Exception as e:
            logger.error(f"Provider registry initialization failed: {e}")
            return ServiceOperationResult(
                success=False,
                message=f"Registry initialization failed: {e}",
                error_code="initialization_failed"
            )
    
    def get_provider(self, provider_name: str) -> Optional[BaseProvider]:
        """
        Get provider by name.
        
        Args:
            provider_name: Provider name
            
        Returns:
            Optional[BaseProvider]: Provider instance or None
        """
        if not self._initialized:
            logger.warning("Registry not initialized, initializing now")
            self.initialize()
        
        provider = self._providers.get(provider_name)
        if not provider:
            logger.warning(f"Provider not found: {provider_name}")
            return None
        
        # Check if provider is healthy
        if not self._health_status.get(provider_name, False):
            logger.warning(f"Provider {provider_name} is unhealthy")
        
        return provider
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available (healthy) providers.
        
        Returns:
            List[str]: List of available provider names
        """
        if not self._initialized:
            self.initialize()
        
        return [
            name for name, provider in self._providers.items()
            if self._health_status.get(name, False)
        ]
    
    def get_primary_provider(self) -> Optional[BaseProvider]:
        """
        Get primary (preferred) provider.
        
        Returns:
            Optional[BaseProvider]: Primary provider or None
        """
        available_providers = self.get_available_providers()
        
        if not available_providers:
            logger.warning("No healthy providers available")
            return None
        
        # Priority order: nowpayments first, then others
        priority_order = ProviderEnum.get_priority_order()
        
        for provider_name in priority_order:
            if provider_name in available_providers:
                return self._providers[provider_name]
        
        # Fallback to first available
        return self._providers[available_providers[0]]
    
    def get_provider_for_currency(self, currency_code: str) -> Optional[BaseProvider]:
        """
        Get best provider for specific currency.
        
        Args:
            currency_code: Currency code
            
        Returns:
            Optional[BaseProvider]: Best provider for currency or None
        """
        available_providers = self.get_available_providers()
        
        # Find providers that support the currency
        supporting_providers = []
        for provider_name in available_providers:
            provider = self._providers[provider_name]
            if currency_code in provider.config.supported_currencies:
                supporting_providers.append(provider)
        
        if not supporting_providers:
            logger.warning(f"No providers support currency: {currency_code}")
            return None
        
        # Return first supporting provider (could be enhanced with more logic)
        return supporting_providers[0]
    
    def health_check_all(self) -> ServiceOperationResult:
        """
        Perform health check on all providers.
        
        Returns:
            ServiceOperationResult: Overall health status
        """
        try:
            logger.debug("Performing health check on all providers")
            
            if not self._providers:
                return ServiceOperationResult(
                    success=False,
                    message="No providers initialized",
                    error_code="no_providers"
                )
            
            health_results = {}
            healthy_count = 0
            
            for provider_name, provider in self._providers.items():
                try:
                    health_result = provider.health_check()
                    is_healthy = health_result.success
                    
                    self._health_status[provider_name] = is_healthy
                    health_results[provider_name] = {
                        'healthy': is_healthy,
                        'message': health_result.message,
                        'data': health_result.data
                    }
                    
                    if is_healthy:
                        healthy_count += 1
                    
                    logger.debug(f"Provider {provider_name} health: {is_healthy}")
                    
                except Exception as e:
                    logger.error(f"Health check failed for {provider_name}: {e}")
                    self._health_status[provider_name] = False
                    health_results[provider_name] = {
                        'healthy': False,
                        'message': f"Health check error: {e}",
                        'data': {}
                    }
            
            overall_healthy = healthy_count > 0
            
            return ServiceOperationResult(
                success=overall_healthy,
                message=f"{healthy_count}/{len(self._providers)} providers healthy",
                data={
                    'total_providers': len(self._providers),
                    'healthy_providers': healthy_count,
                    'unhealthy_providers': len(self._providers) - healthy_count,
                    'provider_health': health_results,
                    'available_providers': self.get_available_providers()
                }
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ServiceOperationResult(
                success=False,
                message=f"Health check error: {e}",
                error_code="health_check_error"
            )
    
    def refresh_configurations(self) -> ServiceOperationResult:
        """
        Refresh provider configurations from config service.
        
        Returns:
            ServiceOperationResult: Refresh result
        """
        try:
            logger.info("Refreshing provider configurations")
            
            # Clear current providers
            self._providers.clear()
            self._health_status.clear()
            self._initialized = False
            
            # Refresh config service
            self.config_service.refresh_configuration()
            
            # Re-initialize providers
            return self.initialize()
            
        except Exception as e:
            logger.error(f"Configuration refresh failed: {e}")
            return ServiceOperationResult(
                success=False,
                message=f"Configuration refresh failed: {e}",
                error_code="refresh_failed"
            )
    
    def get_registry_stats(self) -> ServiceOperationResult:
        """
        Get registry statistics.
        
        Returns:
            ServiceOperationResult: Registry statistics
        """
        try:
            stats = {
                'initialized': self._initialized,
                'total_providers': len(self._providers),
                'healthy_providers': sum(1 for h in self._health_status.values() if h),
                'available_provider_classes': list(self._provider_classes.keys()),
                'configured_providers': list(self._providers.keys()),
                'health_status': dict(self._health_status)
            }
            
            return ServiceOperationResult(
                success=True,
                message="Registry statistics",
                data=stats
            )
            
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return ServiceOperationResult(
                success=False,
                message=f"Stats error: {e}",
                error_code="stats_error"
            )
    
    def _create_provider(self, provider_name: str, config_data: Dict[str, Any]) -> Optional[BaseProvider]:
        """
        Create provider instance from configuration.
        
        Args:
            provider_name: Provider name
            config_data: Provider configuration data
            
        Returns:
            Optional[BaseProvider]: Provider instance or None
        """
        try:
            # Get provider class
            provider_class = self._provider_classes.get(provider_name)
            if not provider_class:
                logger.error(f"Unknown provider class: {provider_name}")
                return None
            
            # Get config class
            config_class = self._provider_configs.get(provider_name)
            if not config_class:
                logger.error(f"Unknown provider config class: {provider_name}")
                return None
            
            # Create configuration
            config = config_class(**config_data)
            
            # Create provider
            provider = provider_class(config)
            
            logger.debug(f"Created provider: {provider}")
            return provider
            
        except Exception as e:
            logger.error(f"Failed to create provider {provider_name}: {e}")
            return None
    
    def register_provider_class(
        self, 
        provider_name: str, 
        provider_class: Type[BaseProvider],
        config_class: Type[ProviderConfig]
    ):
        """
        Register new provider class.
        
        Args:
            provider_name: Provider name
            provider_class: Provider class
            config_class: Provider config class
        """
        self._provider_classes[provider_name] = provider_class
        self._provider_configs[provider_name] = config_class
        logger.info(f"Registered provider class: {provider_name}")
    
    def register_provider(self, provider_name: str, provider_instance: BaseProvider):
        """
        Register provider instance directly (for testing).
        
        Args:
            provider_name: Provider name
            provider_instance: Provider instance
        """
        self._providers[provider_name] = provider_instance
        logger.info(f"Registered provider instance: {provider_name}")
    
    @property
    def providers(self) -> Dict[str, BaseProvider]:
        """Get dictionary of registered providers."""
        return self._providers.copy()
    
    def list_providers(self) -> List[str]:
        """Get list of registered provider names."""
        return list(self._providers.keys())
    
    def __len__(self) -> int:
        """Get number of initialized providers."""
        return len(self._providers)
    
    def __contains__(self, provider_name: str) -> bool:
        """Check if provider is initialized."""
        return provider_name in self._providers
    
    def __iter__(self):
        """Iterate over provider names."""
        return iter(self._providers.keys())


# Global registry instance
_global_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """
    Get global provider registry instance.
    
    Returns:
        ProviderRegistry: Global registry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry


def initialize_providers() -> ServiceOperationResult:
    """
    Initialize global provider registry.
    
    Returns:
        ServiceOperationResult: Initialization result
    """
    registry = get_provider_registry()
    return registry.initialize()
