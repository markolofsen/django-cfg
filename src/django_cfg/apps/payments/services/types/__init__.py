"""
Pydantic types for the Universal Payment System v2.0.

Type-safe models for inter-service communication following data typing requirements.
Uses Pydantic 2 for service layer validation and business logic.
"""

# Request types
from .requests import (
    PaymentCreateRequest,
    PaymentStatusRequest,
    BalanceUpdateRequest,
    SubscriptionCreateRequest,
    SubscriptionUpdateRequest,
    CurrencyConversionRequest,
    WebhookValidationRequest,
)

# Response types  
from .responses import (
    PaymentResult,
    ProviderResponse,
    BalanceResult,
    SubscriptionResult,
    CurrencyConversionResult,
    ServiceOperationResult,
)

# Data types
from .data import (
    PaymentData,
    BalanceData,
    SubscriptionData,
    TransactionData,
    CurrencyData,
    ProviderData,
)

# Webhook types
from .webhooks import (
    WebhookData,
    NowPaymentsWebhook,
    WebhookProcessingResult,
    WebhookSignature,
)

__all__ = [
    # Request types
    'PaymentCreateRequest',
    'PaymentStatusRequest', 
    'BalanceUpdateRequest',
    'SubscriptionCreateRequest',
    'SubscriptionUpdateRequest',
    'CurrencyConversionRequest',
    'WebhookValidationRequest',
    
    # Response types
    'PaymentResult',
    'ProviderResponse',
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
    'ProviderData',
    
    # Webhook types
    'WebhookData',
    'NowPaymentsWebhook',
    'WebhookProcessingResult',
    'WebhookSignature',
]
