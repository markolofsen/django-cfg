"""
Internal Service Types - ONLY for inter-service communication.

DO NOT duplicate Django ORM or DRF! Only for:
1. Providers -> Services (external API response validation)
2. Service -> Service (internal operations)
3. Configuration (settings and parameters)
"""

from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


# =============================================================================
# PROVIDERS - External API response validation
# =============================================================================

class ProviderResponse(BaseModel):
    """Validation for any provider response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool
    provider_payment_id: Optional[str] = None
    payment_url: Optional[str] = None
    pay_amount: Optional[Decimal] = None
    pay_currency: Optional[str] = None
    pay_address: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    # Legacy fields for backward compatibility with tests
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    payment_id: Optional[str] = None
    payment_status: Optional[str] = None
    currency_code: Optional[str] = None


class WebhookData(BaseModel):
    """Provider webhook validation"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider_payment_id: str
    status: str
    pay_amount: Optional[Decimal] = None
    pay_currency: Optional[str] = None
    actually_paid: Optional[Decimal] = None
    order_id: Optional[str] = None
    signature: Optional[str] = None
    error_message: Optional[str] = None


# =============================================================================
# INTER-SERVICE OPERATIONS - Service-to-service typing
# =============================================================================

class ServiceOperationResult(BaseModel):
    """Result of inter-service operation"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class BalanceUpdateRequest(BaseModel):
    """Balance update request between services"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    user_id: int = Field(gt=0)
    amount: Decimal
    source: str
    reference_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessCheckRequest(BaseModel):
    """Access check request between services"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    user_id: int = Field(gt=0)
    endpoint_group: str
    use_cache: bool = True


class AccessCheckResult(BaseModel):
    """Access check result"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    allowed: bool
    subscription_id: Optional[str] = None
    reason: Optional[str] = None
    remaining_requests: Optional[int] = None
    usage_percentage: Optional[float] = None


# =============================================================================
# CONFIGURATION - Service settings
# =============================================================================

class RedisConfig(BaseModel):
    """Redis configuration"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    timeout_seconds: int = 5


class ProviderConfig(BaseModel):
    """Base provider configuration"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    enabled: bool = True
    api_key: str
    sandbox: bool = False
    timeout_seconds: int = 30
    max_retries: int = 3


# =============================================================================
# CACHE OPERATIONS - Minimal cache typing
# =============================================================================

class CacheKey(BaseModel):
    """Cache key typing"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    key: str
    ttl_seconds: Optional[int] = None


class RateLimitResult(BaseModel):
    """Rate limit check result"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    allowed: bool
    remaining: int
    reset_at: datetime
    retry_after_seconds: Optional[int] = None


# =============================================================================
# SERVICE RESPONSE MODELS - Typed responses for service methods
# =============================================================================

class PaymentCreationResult(BaseModel):
    """Payment creation response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool
    payment_id: Optional[str] = None
    provider_payment_id: Optional[str] = None
    payment_url: Optional[str] = None
    error: Optional[str] = None


class WebhookProcessingResult(BaseModel):
    """Webhook processing response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool
    payment_id: Optional[str] = None
    status_updated: bool = False
    balance_updated: bool = False
    error: Optional[str] = None


class PaymentStatusResult(BaseModel):
    """Payment status response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    payment_id: str
    status: str
    amount_usd: Decimal
    currency_code: str
    provider: str
    provider_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserBalanceResult(BaseModel):
    """User balance response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str
    user_id: int
    available_balance: Decimal
    total_balance: Decimal
    reserved_balance: Decimal
    last_updated: datetime
    created_at: datetime


class TransferResult(BaseModel):
    """Funds transfer response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool
    transaction_id: Optional[str] = None
    from_user_id: int
    to_user_id: int
    amount: Decimal
    error: Optional[str] = None
    error_code: Optional[str] = None


class TransactionInfo(BaseModel):
    """Transaction information"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str
    user_id: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    source: str
    reference_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class EndpointGroupInfo(BaseModel):
    """Endpoint group information"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str
    name: str
    display_name: str


class SubscriptionInfo(BaseModel):
    """Subscription information"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str
    endpoint_group: EndpointGroupInfo
    status: str
    tier: str
    monthly_price: Decimal
    usage_current: int
    usage_limit: int
    usage_percentage: float
    remaining_requests: int
    expires_at: datetime
    next_billing: Optional[datetime] = None
    created_at: datetime


class SubscriptionAnalytics(BaseModel):
    """Subscription analytics response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    period: Dict[str, Any] = Field(default_factory=dict)
    total_revenue: Decimal
    active_subscriptions: int
    new_subscriptions: int
    churned_subscriptions: int
    error: Optional[str] = None


# =============================================================================
# ADDITIONAL RESPONSE MODELS - Missing Pydantic models
# =============================================================================

class PaymentHistoryItem(BaseModel):
    """Single payment item for history lists"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str
    user_id: int
    amount: Decimal
    currency: str
    status: str
    provider: str
    provider_payment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderInfo(BaseModel):
    """Payment provider information"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    name: str
    display_name: str
    supported_currencies: list[str] = Field(default_factory=list)
    is_active: bool
    features: Dict[str, Any] = Field(default_factory=dict)
