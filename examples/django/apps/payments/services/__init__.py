"""
Services package for the Universal Payment System v2.0.

Business logic services with Pydantic validation and type safety.
"""

# Core services
from .core import (
    BaseService,
    PaymentService,
    BalanceService,
    SubscriptionService,
    WebhookService,
    CurrencyService,
)

# Service types
from .types import (
    # Request types
    PaymentCreateRequest,
    PaymentStatusRequest,
    BalanceUpdateRequest,
    SubscriptionCreateRequest,
    SubscriptionUpdateRequest,
    CurrencyConversionRequest,
    
    # Response types
    PaymentResult,
    BalanceResult,
    SubscriptionResult,
    CurrencyConversionResult,
    ServiceOperationResult,
    
    # Data types
    PaymentData,
    BalanceData,
    SubscriptionData,
    TransactionData,
    CurrencyData,
    
    # Webhook types
    WebhookData,
    NowPaymentsWebhook,
    WebhookProcessingResult,
)

__all__ = [
    # Core services
    'BaseService',
    'PaymentService',
    'BalanceService',
    'SubscriptionService',
    'WebhookService',
    'CurrencyService',
    
    # Request types
    'PaymentCreateRequest',
    'PaymentStatusRequest',
    'BalanceUpdateRequest',
    'SubscriptionCreateRequest',
    'SubscriptionUpdateRequest',
    'CurrencyConversionRequest',
    
    # Response types
    'PaymentResult',
    'BalanceResult',
    'SubscriptionResult',
    'CurrencyConversionResult',
    'ServiceOperationResult',
    
    # Data types
    'PaymentData',
    'BalanceData',
    'SubscriptionData',
    'TransactionData',
    'CurrencyData',
    
    # Webhook types
    'WebhookData',
    'NowPaymentsWebhook',
    'WebhookProcessingResult',
]


# Service registry for dependency injection and health checks
class ServiceRegistry:
    """
    Service registry for managing service instances.
    
    Provides singleton access to services and health monitoring.
    """
    
    _instances = {}
    
    @classmethod
    def get_payment_service(cls) -> PaymentService:
        """Get PaymentService instance."""
        if 'payment' not in cls._instances:
            cls._instances['payment'] = PaymentService()
        return cls._instances['payment']
    
    @classmethod
    def get_balance_service(cls) -> BalanceService:
        """Get BalanceService instance."""
        if 'balance' not in cls._instances:
            cls._instances['balance'] = BalanceService()
        return cls._instances['balance']
    
    @classmethod
    def get_subscription_service(cls) -> SubscriptionService:
        """Get SubscriptionService instance."""
        if 'subscription' not in cls._instances:
            cls._instances['subscription'] = SubscriptionService()
        return cls._instances['subscription']
    
    @classmethod
    def get_webhook_service(cls) -> WebhookService:
        """Get WebhookService instance."""
        if 'webhook' not in cls._instances:
            cls._instances['webhook'] = WebhookService()
        return cls._instances['webhook']
    
    @classmethod
    def get_currency_service(cls) -> CurrencyService:
        """Get CurrencyService instance."""
        if 'currency' not in cls._instances:
            cls._instances['currency'] = CurrencyService()
        return cls._instances['currency']
    
    @classmethod
    def get_all_services(cls) -> dict:
        """Get all service instances."""
        return {
            'payment': cls.get_payment_service(),
            'balance': cls.get_balance_service(),
            'subscription': cls.get_subscription_service(),
            'webhook': cls.get_webhook_service(),
            'currency': cls.get_currency_service(),
        }
    
    @classmethod
    def health_check_all(cls) -> dict:
        """Perform health check on all services."""
        services = cls.get_all_services()
        results = {}
        
        for name, service in services.items():
            try:
                health_result = service.health_check()
                results[name] = {
                    'healthy': health_result.success,
                    'message': health_result.message,
                    'data': health_result.data
                }
            except Exception as e:
                results[name] = {
                    'healthy': False,
                    'message': f"Health check failed: {e}",
                    'data': {}
                }
        
        return results
    
    @classmethod
    def clear_cache_all(cls):
        """Clear cache for all services."""
        for service in cls._instances.values():
            if hasattr(service, '_cache_clear'):
                service._cache_clear()
    
    @classmethod
    def get_stats_all(cls) -> dict:
        """Get statistics from all services."""
        services = cls.get_all_services()
        stats = {}
        
        for name, service in services.items():
            try:
                service_stats = service.get_service_stats()
                stats[name] = service_stats
            except Exception as e:
                stats[name] = {
                    'error': str(e),
                    'service_name': service.__class__.__name__
                }
        
        return stats


# Convenience functions for direct service access
def get_payment_service() -> PaymentService:
    """Get PaymentService instance."""
    return ServiceRegistry.get_payment_service()


def get_balance_service() -> BalanceService:
    """Get BalanceService instance."""
    return ServiceRegistry.get_balance_service()


def get_subscription_service() -> SubscriptionService:
    """Get SubscriptionService instance."""
    return ServiceRegistry.get_subscription_service()


def get_webhook_service() -> WebhookService:
    """Get WebhookService instance."""
    return ServiceRegistry.get_webhook_service()


def get_currency_service() -> CurrencyService:
    """Get CurrencyService instance."""
    return ServiceRegistry.get_currency_service()


# Add convenience functions to __all__
__all__.extend([
    'ServiceRegistry',
    'get_payment_service',
    'get_balance_service',
    'get_subscription_service',
    'get_webhook_service',
    'get_currency_service',
])
