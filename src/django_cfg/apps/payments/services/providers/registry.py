"""
Provider registry for managing payment providers.

Central registry with lazy loading and typed configuration.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from django.core.cache import cache
from django.utils import timezone

from .base import PaymentProvider
from ...utils.config_utils import get_payments_config
from .nowpayments.provider import NowPaymentsProvider
from .nowpayments.models import NowPaymentsConfig
from .cryptapi.provider import CryptAPIProvider
from .cryptapi.models import CryptAPIConfig
from .cryptomus.provider import CryptomusProvider
from .cryptomus.models import CryptomusConfig
from .stripe.provider import StripeProvider
from .stripe.models import StripeConfig
from django_cfg.modules.django_logger import get_logger

logger = get_logger("provider_registry")


class ProviderRegistry:
    """Central registry for payment providers with typed configs."""
    
    def __init__(self):
        """Initialize registry with lazy loading and health monitoring."""
        self._providers: dict[str, PaymentProvider] = {}
        self._provider_configs: dict[str, dict] = {}
        self._health_cache: dict[str, dict] = {}
        self._fallback_order: List[str] = []  # Provider preference order
        self._load_configurations()
        self._initialize_health_monitoring()
    
    def _load_configurations(self) -> None:
        """Load provider configurations."""
        try:
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
                config = StripeConfig(**config_dict)
                return StripeProvider(config)
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
            if provider and provider.enabled:
                active.append(name)
        return active
    
    def _initialize_health_monitoring(self) -> None:
        """Initialize health monitoring for all providers."""
        try:
            # Set up fallback order based on configuration or defaults
            available_providers = self.list_providers()
            
            # Default priority: NowPayments -> CryptAPI -> Cryptomus -> Stripe
            priority_order = ['nowpayments', 'cryptapi', 'cryptomus', 'stripe']
            
            self._fallback_order = [p for p in priority_order if p in available_providers]
            
            # Add any other providers not in priority list
            for provider in available_providers:
                if provider not in self._fallback_order:
                    self._fallback_order.append(provider)
                    
            logger.info(f"Initialized provider fallback order: {self._fallback_order}")
            
        except Exception as e:
            logger.error(f"Error initializing health monitoring: {e}")
            self._fallback_order = []
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Check health of all providers with performance metrics.
        
        Returns:
            Dict mapping provider names to health status
        """
        results = {}
        
        for provider_name in self.list_providers():
            try:
                provider = self.get_provider(provider_name)
                if not provider:
                    results[provider_name] = {
                        'status': 'unavailable',
                        'error': 'Provider not loaded',
                        'last_check': timezone.now().isoformat()
                    }
                    continue
                
                # Measure response time
                start_time = time.time()
                
                try:
                    # Use get_supported_currencies as health check endpoint
                    health_response = provider.get_supported_currencies()
                    response_time = int((time.time() - start_time) * 1000)  # ms
                    
                    if health_response.success:
                        status = 'healthy'
                        error = None
                    else:
                        status = 'degraded'
                        error = health_response.error_message
                        
                except Exception as provider_error:
                    response_time = int((time.time() - start_time) * 1000)  # ms
                    status = 'unhealthy'
                    error = str(provider_error)
                
                # Cache health status
                health_data = {
                    'status': status,
                    'response_time_ms': response_time,
                    'error': error,
                    'last_check': timezone.now().isoformat(),
                    'provider_enabled': provider.enabled
                }
                
                # Store in cache for 5 minutes
                cache_key = f"provider_health:{provider_name}"
                cache.set(cache_key, health_data, timeout=300)
                
                results[provider_name] = health_data
                
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {e}")
                results[provider_name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_check': timezone.now().isoformat()
                }
        
        return results
    
    def get_healthy_providers(self, operation: str = None) -> List[str]:
        """
        Get list of healthy providers in fallback order.
        
        Args:
            operation: Specific operation (e.g., 'payment_creation', 'webhook')
            
        Returns:
            List of provider names sorted by health and priority
        """
        healthy_providers = []
        
        for provider_name in self._fallback_order:
            # Check cached health status
            cache_key = f"provider_health:{provider_name}"
            health_data = cache.get(cache_key)
            
            if health_data and health_data.get('status') in ['healthy', 'degraded']:
                provider = self.get_provider(provider_name)
                if provider and provider.enabled:
                    healthy_providers.append(provider_name)
        
        return healthy_providers
    
    def get_provider_with_fallback(self, preferred_provider: str = None, operation: str = None) -> Optional[PaymentProvider]:
        """
        Get provider with automatic fallback to healthy alternatives.
        
        Args:
            preferred_provider: Preferred provider name
            operation: Operation type for provider selection
            
        Returns:
            PaymentProvider instance or None if all providers are down
        """
        # Start with preferred provider if specified and healthy
        if preferred_provider:
            provider = self.get_provider(preferred_provider)
            if provider and provider.enabled:
                # Quick health check from cache
                cache_key = f"provider_health:{preferred_provider}"
                health_data = cache.get(cache_key)
                
                if not health_data or health_data.get('status') in ['healthy', 'degraded']:
                    logger.info(f"Using preferred provider: {preferred_provider}")
                    return provider
                else:
                    logger.warning(f"Preferred provider {preferred_provider} is unhealthy, falling back")
        
        # Fallback to healthy providers in order
        healthy_providers = self.get_healthy_providers(operation)
        
        for provider_name in healthy_providers:
            provider = self.get_provider(provider_name)
            if provider:
                logger.info(f"Using fallback provider: {provider_name}")
                return provider
        
        logger.error("No healthy providers available!")
        return None
    
    def record_provider_performance(self, provider_name: str, operation: str, 
                                  response_time_ms: int, success: bool) -> None:
        """
        Record provider performance metrics.
        
        Args:
            provider_name: Name of the provider
            operation: Operation performed (e.g., 'create_payment', 'check_status')
            response_time_ms: Response time in milliseconds
            success: Whether operation was successful
        """
        try:
            # Store performance metrics in cache
            metric_key = f"provider_metrics:{provider_name}:{operation}"
            
            # Get current metrics
            current_metrics = cache.get(metric_key, {
                'total_requests': 0,
                'successful_requests': 0,
                'average_response_time': 0,
                'last_updated': timezone.now().isoformat()
            })
            
            # Update metrics
            total_requests = current_metrics['total_requests'] + 1
            successful_requests = current_metrics['successful_requests'] + (1 if success else 0)
            
            # Calculate rolling average response time
            current_avg = current_metrics['average_response_time']
            new_avg = ((current_avg * current_metrics['total_requests']) + response_time_ms) / total_requests
            
            updated_metrics = {
                'total_requests': total_requests,
                'successful_requests': successful_requests,
                'success_rate': (successful_requests / total_requests) * 100,
                'average_response_time': int(new_avg),
                'last_response_time': response_time_ms,
                'last_updated': timezone.now().isoformat()
            }
            
            # Store for 24 hours
            cache.set(metric_key, updated_metrics, timeout=86400)
            
            # Log performance issues
            if not success:
                logger.warning(f"Provider {provider_name} operation {operation} failed (response time: {response_time_ms}ms)")
            elif response_time_ms > 5000:  # > 5 seconds
                logger.warning(f"Provider {provider_name} operation {operation} slow (response time: {response_time_ms}ms)")
                
        except Exception as e:
            logger.error(f"Error recording provider performance: {e}")
    
    def get_provider_metrics(self, provider_name: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Get performance metrics for providers.
        
        Args:
            provider_name: Specific provider or None for all providers
            
        Returns:
            Dict of provider metrics
        """
        if provider_name:
            providers_to_check = [provider_name]
        else:
            providers_to_check = self.list_providers()
        
        metrics = {}
        
        for provider in providers_to_check:
            provider_metrics = {}
            
            # Common operations to check
            operations = ['create_payment', 'check_status', 'process_webhook', 'get_currencies']
            
            for operation in operations:
                metric_key = f"provider_metrics:{provider}:{operation}"
                operation_metrics = cache.get(metric_key)
                
                if operation_metrics:
                    provider_metrics[operation] = operation_metrics
            
            if provider_metrics:
                metrics[provider] = provider_metrics
        
        return metrics
    
    def reload_providers(self) -> None:
        """Reload all providers from configuration."""
        logger.info("Reloading providers from configuration")
        self._providers.clear()
        self._load_configurations()


# Global singleton instance  
_registry_instance = None

def get_provider_registry() -> ProviderRegistry:
    """Get global provider registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ProviderRegistry()
    return _registry_instance


def get_payment_provider(provider_name: str) -> Optional[PaymentProvider]:
    """
    Get payment provider instance by name.
    
    Args:
        provider_name: Name of provider (e.g. 'nowpayments', 'stripe')
        
    Returns:
        Provider instance or None if not found
    """
    registry = get_provider_registry()
    return registry.get_provider(provider_name)


def get_available_providers() -> List[str]:
    """
    Get list of available provider names.
    
    Returns:
        List of provider names that are configured
    """
    registry = get_provider_registry()
    return registry.list_providers()
