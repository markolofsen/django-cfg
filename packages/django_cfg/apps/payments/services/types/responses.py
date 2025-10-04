"""
Response types for the Universal Payment System v2.0.

Pydantic models for service layer responses and results.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ServiceOperationResult(BaseModel):
    """
    Base result type for all service operations.
    
    Provides consistent success/error handling across services.
    """
    model_config = ConfigDict(validate_assignment=True)
    
    success: bool = Field(description="Operation success status")
    message: Optional[str] = Field(None, description="Human-readable message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional result data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")


class PaymentResult(ServiceOperationResult):
    """Result of payment operations."""
    
    payment_id: Optional[str] = Field(None, description="Payment ID")
    status: Optional[str] = Field(None, description="Payment status")
    amount_usd: Optional[float] = Field(None, description="Payment amount in USD")
    crypto_amount: Optional[Decimal] = Field(None, description="Crypto amount")
    currency_code: Optional[str] = Field(None, description="Cryptocurrency code")
    provider_payment_id: Optional[str] = Field(None, description="Provider payment ID")
    payment_url: Optional[str] = Field(None, description="Payment URL")
    qr_code_url: Optional[str] = Field(None, description="QR code URL")
    wallet_address: Optional[str] = Field(None, description="Wallet address")
    expires_at: Optional[datetime] = Field(None, description="Payment expiration")


class ProviderResponse(BaseModel):
    """Response from payment provider."""
    model_config = ConfigDict(validate_assignment=True)
    
    provider: str = Field(description="Provider name")
    success: bool = Field(description="Provider operation success")
    provider_payment_id: Optional[str] = Field(None, description="Provider payment ID")
    status: Optional[str] = Field(None, description="Provider status")
    amount: Optional[Decimal] = Field(None, description="Amount from provider")
    currency: Optional[str] = Field(None, description="Currency from provider")
    payment_url: Optional[str] = Field(None, description="Payment URL")
    wallet_address: Optional[str] = Field(None, description="Wallet address")
    qr_code_url: Optional[str] = Field(None, description="QR code URL")
    expires_at: Optional[datetime] = Field(None, description="Payment expiration")
    error_message: Optional[str] = Field(None, description="Error message")
    raw_response: Dict[str, Any] = Field(default_factory=dict, description="Raw provider response")


class BalanceResult(ServiceOperationResult):
    """Result of balance operations."""
    
    user_id: Optional[int] = Field(None, description="User ID")
    balance_usd: Optional[float] = Field(None, description="Current balance in USD")
    transaction_id: Optional[str] = Field(None, description="Transaction ID")
    transaction_amount: Optional[float] = Field(None, description="Transaction amount")
    transaction_type: Optional[str] = Field(None, description="Transaction type")


class SubscriptionResult(ServiceOperationResult):
    """Result of subscription operations."""
    
    subscription_id: Optional[str] = Field(None, description="Subscription ID")
    user_id: Optional[int] = Field(None, description="User ID")
    tier: Optional[str] = Field(None, description="Subscription tier")
    status: Optional[str] = Field(None, description="Subscription status")
    expires_at: Optional[datetime] = Field(None, description="Subscription expiration")
    requests_remaining: Optional[int] = Field(None, description="Requests remaining today")


class CurrencyConversionResult(ServiceOperationResult):
    """Result of currency conversion."""
    
    amount: Optional[float] = Field(None, description="Original amount")
    from_currency: Optional[str] = Field(None, description="Source currency")
    to_currency: Optional[str] = Field(None, description="Target currency")
    converted_amount: Optional[float] = Field(None, description="Converted amount")
    exchange_rate: Optional[float] = Field(None, description="Exchange rate used")
    rate_timestamp: Optional[datetime] = Field(None, description="Rate timestamp")


class APIKeyResult(ServiceOperationResult):
    """Result of API key operations."""
    
    api_key_id: Optional[str] = Field(None, description="API key ID")
    key_value: Optional[str] = Field(None, description="API key value (only on creation)")
    name: Optional[str] = Field(None, description="API key name")
    is_active: Optional[bool] = Field(None, description="API key active status")
    expires_at: Optional[datetime] = Field(None, description="API key expiration")
    total_requests: Optional[int] = Field(None, description="Total requests made")


class WebhookProcessingResult(ServiceOperationResult):
    """Result of webhook processing."""
    
    webhook_id: Optional[str] = Field(None, description="Webhook ID")
    provider: Optional[str] = Field(None, description="Provider name")
    payment_id: Optional[str] = Field(None, description="Related payment ID")
    processed: bool = Field(default=False, description="Whether webhook was processed")
    actions_taken: List[str] = Field(default_factory=list, description="Actions taken during processing")


class ProviderHealthResult(ServiceOperationResult):
    """Result of provider health check."""
    
    provider: str = Field(description="Provider name")
    is_healthy: bool = Field(description="Provider health status")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    api_status: Optional[str] = Field(None, description="API status")
    rates_available: Optional[bool] = Field(None, description="Currency rates availability")
    last_successful_call: Optional[datetime] = Field(None, description="Last successful API call")
    error_details: Optional[str] = Field(None, description="Error details if unhealthy")


class ServiceStats(BaseModel):
    """Service statistics."""
    model_config = ConfigDict(validate_assignment=True)
    
    service_name: str = Field(description="Service name")
    total_operations: int = Field(default=0, description="Total operations")
    successful_operations: int = Field(default=0, description="Successful operations")
    failed_operations: int = Field(default=0, description="Failed operations")
    success_rate: float = Field(default=0.0, description="Success rate percentage")
    avg_response_time_ms: Optional[float] = Field(None, description="Average response time")
    last_operation: Optional[datetime] = Field(None, description="Last operation timestamp")
    uptime_seconds: Optional[int] = Field(None, description="Service uptime in seconds")


class BatchOperationResult(ServiceOperationResult):
    """Result of batch operations."""
    
    total_items: int = Field(description="Total items processed")
    successful_items: int = Field(description="Successfully processed items")
    failed_items: int = Field(description="Failed items")
    results: List[ServiceOperationResult] = Field(default_factory=list, description="Individual results")
    processing_time_ms: Optional[int] = Field(None, description="Total processing time")


class CacheOperationResult(ServiceOperationResult):
    """Result of cache operations."""
    
    cache_key: Optional[str] = Field(None, description="Cache key")
    cache_hit: Optional[bool] = Field(None, description="Whether cache was hit")
    ttl_seconds: Optional[int] = Field(None, description="TTL in seconds")
    data_size_bytes: Optional[int] = Field(None, description="Data size in bytes")
