"""
Request types for the Universal Payment System v2.0.

Pydantic models for validating incoming service requests.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


class PaymentCreateRequest(BaseModel):
    """
    Type-safe payment creation request.
    
    Used for validating payment creation across all service layers.
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True
    )
    
    user_id: int = Field(gt=0, description="User ID")
    amount_usd: float = Field(gt=1.0, le=50000.0, description="Amount in USD")
    currency_code: str = Field(
        min_length=2, max_length=10, description="Cryptocurrency code"
    )
    provider: Literal['nowpayments'] = Field(default='nowpayments', description="Payment provider")
    callback_url: Optional[str] = Field(None, description="Success callback URL")
    cancel_url: Optional[str] = Field(None, description="Cancellation URL") 
    description: Optional[str] = Field(None, max_length=500, description="Payment description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('currency_code')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency is supported by checking database."""
        from django_cfg.apps.payments.models import Currency
        
        currency_code = v.upper().strip()
        
        # Check if currency exists in database and is active
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)
            return currency_code
        except Currency.DoesNotExist:
            # Get list of active currencies for error message
            active_currencies = Currency.objects.filter(is_active=True).values_list('code', flat=True)[:10]
            currency_list = ', '.join(active_currencies) + ('...' if len(active_currencies) == 10 else '')
            raise ValueError(f"Currency {currency_code} not found or inactive. Available: {currency_list}")
        except Exception:
            # Fallback validation if database is not available
            return currency_code
    
    @field_validator('callback_url', 'cancel_url')
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Validate URLs if provided."""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("URLs must start with http:// or https://")
        return v


class PaymentStatusRequest(BaseModel):
    """Request for checking payment status."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    payment_id: str = Field(description="Payment ID to check")
    user_id: Optional[int] = Field(None, description="User ID for authorization")
    force_provider_check: bool = Field(default=False, description="Force check with provider")


class BalanceUpdateRequest(BaseModel):
    """Request for updating user balance."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    user_id: int = Field(gt=0, description="User ID")
    amount: float = Field(description="Amount to add/subtract (positive=add, negative=subtract)")
    transaction_type: Literal['deposit', 'withdrawal', 'payment', 'refund', 'fee', 'bonus', 'adjustment'] = Field(
        description="Type of transaction"
    )
    description: Optional[str] = Field(None, description="Transaction description")
    payment_id: Optional[str] = Field(None, description="Related payment ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        """Validate amount is not zero."""
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v


class SubscriptionCreateRequest(BaseModel):
    """Request for creating subscription."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    user_id: int = Field(gt=0, description="User ID")
    tier: Literal['free', 'basic', 'pro', 'enterprise'] = Field(description="Subscription tier")
    duration_days: int = Field(default=30, gt=0, le=365, description="Subscription duration in days")
    auto_renew: bool = Field(default=False, description="Enable auto-renewal")
    endpoint_groups: list[str] = Field(default_factory=list, description="Endpoint group codes")


class SubscriptionUpdateRequest(BaseModel):
    """Request for updating subscription."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    subscription_id: int = Field(gt=0, description="Subscription ID")
    tier: Optional[Literal['free', 'basic', 'pro', 'enterprise']] = Field(None, description="New subscription tier")
    duration_days: Optional[int] = Field(None, gt=0, le=365, description="New duration in days")
    auto_renew: Optional[bool] = Field(None, description="Enable/disable auto-renewal")
    endpoint_groups: Optional[list[str]] = Field(None, description="New endpoint group codes")


class CurrencyConversionRequest(BaseModel):
    """Request for currency conversion."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    amount: float = Field(gt=0, description="Amount to convert")
    from_currency: str = Field(min_length=3, max_length=10, description="Source currency code")
    to_currency: str = Field(min_length=3, max_length=10, description="Target currency code")
    
    @field_validator('from_currency', 'to_currency')
    @classmethod
    def validate_currency_codes(cls, v: str) -> str:
        """Normalize currency codes."""
        return v.upper().strip()


class APIKeyCreateRequest(BaseModel):
    """Request for creating API key."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    user_id: int = Field(gt=0, description="User ID")
    name: str = Field(min_length=1, max_length=100, description="API key name")
    expires_in_days: Optional[int] = Field(None, gt=0, le=365, description="Days until expiration")
    allowed_ips: Optional[str] = Field(None, description="Comma-separated allowed IP addresses")


class WebhookValidationRequest(BaseModel):
    """Request for webhook validation."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider: str = Field(description="Provider name")
    payload: Dict[str, Any] = Field(description="Webhook payload")
    signature: Optional[str] = Field(None, description="Webhook signature")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    timestamp: Optional[str] = Field(None, description="Request timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    
    
class ProviderHealthCheckRequest(BaseModel):
    """Request for provider health check."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider: str = Field(description="Provider name to check")
    include_rates: bool = Field(default=False, description="Include currency rates in check")
    timeout: int = Field(default=30, gt=0, le=300, description="Timeout in seconds")
