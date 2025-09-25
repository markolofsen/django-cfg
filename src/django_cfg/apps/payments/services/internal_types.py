"""
Internal Service Types - ONLY for inter-service communication.

DO NOT duplicate Django ORM or DRF! Only for:
1. Providers -> Services (external API response validation)
2. Service -> Service (internal operations)
3. Configuration (settings and parameters)
"""

from pydantic import BaseModel, Field, ConfigDict, computed_field
from decimal import Decimal
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from django_cfg.modules.django_logger import get_logger

logger = get_logger("internal_types")




# =============================================================================
# UNIVERSAL CURRENCY MODEL - for provider → base communication
# =============================================================================

class UniversalCurrency(BaseModel):
    """Universal currency model that all providers should return."""
    model_config = ConfigDict(validate_assignment=True, extra="allow")
    
    # Core identification
    provider_currency_code: str = Field(..., description="Original provider code: USDTERC20, USDTBSC, BTC")
    base_currency_code: str = Field(..., description="Parsed base currency: USDT, BTC")
    network_code: Optional[str] = Field(None, description="Parsed network: ethereum, bsc, bitcoin")
    
    # Display info
    name: str = Field(..., description="Human readable name")
    currency_type: str = Field(default="crypto", description="fiat or crypto")
    
    # Provider flags
    is_enabled: bool = Field(default=True, description="Available for use")
    is_popular: bool = Field(default=False, description="Popular currency")
    is_stable: bool = Field(default=False, description="Stablecoin")
    priority: int = Field(default=0, description="Display priority")
    
    # URLs and assets
    logo_url: str = Field(default="", description="Logo URL")
    
    # Limits and availability  
    available_for_payment: bool = Field(default=True, description="Can receive payments")
    available_for_payout: bool = Field(default=True, description="Can send payouts")
    min_amount: Optional[float] = Field(None, description="Minimum amount")
    max_amount: Optional[float] = Field(None, description="Maximum amount")
    
    # Raw provider data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Original provider response")


class UniversalCurrenciesResponse(BaseModel):
    """Universal response with parsed currencies."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies: List[UniversalCurrency] = Field(..., description="Parsed currencies")


# =============================================================================
# SYNCHRONIZATION RESULTS - Typed sync operation results
# =============================================================================

class ProviderSyncResult(BaseModel):
    """Result of provider synchronization operation."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Currencies operations
    currencies_created: int = Field(default=0, description="Number of new currencies created")
    currencies_updated: int = Field(default=0, description="Number of existing currencies updated")
    
    # Networks operations  
    networks_created: int = Field(default=0, description="Number of new networks created")
    networks_updated: int = Field(default=0, description="Number of existing networks updated")
    
    # Provider currencies operations
    provider_currencies_created: int = Field(default=0, description="Number of new provider currencies created")
    provider_currencies_updated: int = Field(default=0, description="Number of existing provider currencies updated")
    
    # Error tracking
    errors: List[str] = Field(default_factory=list, description="List of errors encountered during sync")
    
    @property
    def total_items_processed(self) -> int:
        """Get total number of items processed."""
        return (
            self.currencies_created + self.currencies_updated +
            self.networks_created + self.networks_updated +
            self.provider_currencies_created + self.provider_currencies_updated
        )
    
    @property
    def success(self) -> bool:
        """Check if sync completed without errors."""
        return len(self.errors) == 0
    
    @property
    def has_changes(self) -> bool:
        """Check if any changes were made."""
        return self.total_items_processed > 0


# AJAX Response Types
class CurrencyOptionModel(BaseModel):
    """Single currency option for UI select dropdown."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider_currency_code: str = Field(..., description="Provider-specific currency code")
    display_name: str = Field(..., description="Human-readable display name")
    base_currency_code: str = Field(..., description="Normalized base currency code")
    base_currency_name: str = Field(..., description="Base currency full name")
    network_code: Optional[str] = Field(None, description="Network code if applicable")
    network_name: Optional[str] = Field(None, description="Network full name if applicable")
    currency_type: str = Field(..., description="Currency type: crypto or fiat")
    is_popular: bool = Field(default=False, description="Is this a popular currency")
    is_stable: bool = Field(default=False, description="Is this a stablecoin")
    available_for_payment: bool = Field(default=True, description="Available for payments")
    available_for_payout: bool = Field(default=True, description="Available for payouts")
    min_amount: Optional[str] = Field(None, description="Minimum amount as string")
    max_amount: Optional[str] = Field(None, description="Maximum amount as string")
    logo_url: Optional[str] = Field(None, description="Currency logo URL")
    # Exchange rates
    usd_rate: float = Field(default=0.0, description="1 CURRENCY = X USD")
    tokens_per_usd: float = Field(default=0.0, description="How many tokens for 1 USD")


class ProviderCurrencyOptionsResponse(BaseModel):
    """Response for provider currency options API."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool = Field(..., description="API call success status")
    provider: str = Field(..., description="Provider name")
    currency_options: List[CurrencyOptionModel] = Field(default_factory=list, description="Available currency options")
    count: int = Field(..., description="Number of currency options")
    error: Optional[str] = Field(None, description="Error message if any")


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
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Legacy fields for backward compatibility with tests
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    payment_id: Optional[str] = None
    payment_status: Optional[str] = None
    currency_code: Optional[str] = None


class PaymentAmountEstimate(BaseModel):
    """Universal payment amount estimation response"""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency_from: str = Field(description="Source currency code")
    currency_to: str = Field(description="Target currency code") 
    amount_from: Decimal = Field(gt=0, description="Source amount")
    estimated_amount: Decimal = Field(gt=0, description="Estimated target amount")
    fee_amount: Optional[Decimal] = Field(None, ge=0, description="Provider fee amount")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate used")
    provider_name: str = Field(description="Provider that made the estimation")
    estimated_at: Optional[datetime] = Field(None, description="When estimation was made")


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
    """Base provider configuration with automatic sandbox detection"""
    model_config = ConfigDict(validate_assignment=True, extra="allow")  # Allow extra fields for flexibility
    
    enabled: bool = True
    api_key: str
    timeout_seconds: int = Field(default=30, alias='timeout', description="Request timeout in seconds")
    max_retries: int = 3
    
    @computed_field
    @property
    def sandbox(self) -> bool:
        """Get sandbox mode from django-cfg config."""
        try:
            from django_cfg.core.config import get_current_config
            current_config = get_current_config()
            
            if current_config:
                # Check env_mode first
                if hasattr(current_config, 'env_mode'):
                    env_mode = current_config.env_mode
                    if isinstance(env_mode, str):
                        return env_mode.lower() in ['development', 'dev', 'test']
                
                # Fallback to debug flag
                if hasattr(current_config, 'debug'):
                    return current_config.debug
            
            return True  # Default to sandbox for safety
        except Exception:
            return True


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