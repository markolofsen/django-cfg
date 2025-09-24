"""
Universal Payment Services.

Modular architecture with minimal Pydantic typing for inter-service communication.
Uses Django ORM for data persistence and DRF for API responses.
"""

# Core services
from .core.payment_service import PaymentService
from .core.balance_service import BalanceService
from .core.subscription_service import SubscriptionService

# Provider services
from .providers.registry import ProviderRegistry
from .providers.nowpayments import NowPaymentsProvider
from .providers.cryptapi import CryptAPIProvider

# Cache services
from .cache import SimpleCache, ApiKeyCache, RateLimitCache

# Internal types for inter-service communication
from .internal_types import (
    ProviderResponse, WebhookData, ServiceOperationResult,
    BalanceUpdateRequest, AccessCheckRequest, AccessCheckResult,
    # Service response models
    PaymentCreationResult, WebhookProcessingResult, PaymentStatusResult,
    UserBalanceResult, TransferResult, TransactionInfo,
    EndpointGroupInfo, SubscriptionInfo, SubscriptionAnalytics,
    # Additional response models
    PaymentHistoryItem, ProviderInfo
)

__all__ = [
    # Core services
    'PaymentService',
    'BalanceService', 
    'SubscriptionService',
    
    # Provider services
    'ProviderRegistry',
    'NowPaymentsProvider',
    'CryptAPIProvider',
    
    # Cache services
    'SimpleCache',
    'ApiKeyCache', 
    'RateLimitCache',
    
    # Internal types
    'ProviderResponse',
    'WebhookData', 
    'ServiceOperationResult',
    'BalanceUpdateRequest',
    'AccessCheckRequest',
    'AccessCheckResult',
    
    # Service response models
    'PaymentCreationResult',
    'WebhookProcessingResult', 
    'PaymentStatusResult',
    'UserBalanceResult',
    'TransferResult',
    'TransactionInfo',
    'EndpointGroupInfo',
    'SubscriptionInfo',
    'SubscriptionAnalytics',
    
    # Additional response models
    'PaymentHistoryItem',
    'ProviderInfo',
]
