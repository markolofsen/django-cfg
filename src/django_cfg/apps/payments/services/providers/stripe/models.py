from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ...internal_types import ProviderConfig


class StripeConfig(ProviderConfig):
    """Stripe provider configuration with Pydantic v2."""
    
    webhook_secret: Optional[str] = Field(None, description="Webhook endpoint secret")
    success_url: Optional[str] = Field(None, description="Payment success redirect URL")
    cancel_url: Optional[str] = Field(None, description="Payment cancel redirect URL")
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or not v.startswith(('sk_test_', 'sk_live_')):
            raise ValueError("Stripe API key must start with sk_test_ or sk_live_")
        return v


class StripeCurrency(BaseModel):
    """Stripe specific currency model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency_code: str = Field(..., description="Currency symbol (e.g., USD, EUR)")
    name: str = Field(..., description="Full currency name")
    decimal_digits: int = Field(..., description="Number of decimal digits")
    min_amount: Optional[Decimal] = Field(None, description="Minimum charge amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum charge amount")
    is_zero_decimal: bool = Field(False, description="Zero-decimal currency (like JPY)")


class StripeNetwork(BaseModel):
    """Stripe network model (not applicable for fiat payments)."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    code: str = Field(..., description="Network code (always 'stripe')")
    name: str = Field(..., description="Network display name")
    currency: str = Field(..., description="Currency this network belongs to")


class StripePaymentIntentRequest(BaseModel):
    """Stripe PaymentIntent creation request."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    amount: int = Field(..., description="Amount in smallest currency unit")
    currency: str = Field(..., description="Three-letter ISO currency code")
    payment_method_types: List[str] = Field(default=["card"], description="Payment method types")
    confirm: bool = Field(False, description="Confirm PaymentIntent immediately")
    capture_method: str = Field("automatic", description="Capture method")
    confirmation_method: str = Field("automatic", description="Confirmation method")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, str]] = Field(None, description="Metadata")
    receipt_email: Optional[str] = Field(None, description="Receipt email")
    return_url: Optional[str] = Field(None, description="Return URL")
    success_url: Optional[str] = Field(None, description="Success URL")
    cancel_url: Optional[str] = Field(None, description="Cancel URL")


class StripePaymentIntentResponse(BaseModel):
    """Stripe PaymentIntent response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str = Field(..., description="PaymentIntent ID")
    object: str = Field(..., description="Object type")
    amount: int = Field(..., description="Amount in smallest currency unit")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="PaymentIntent status")
    client_secret: str = Field(..., description="Client secret for confirmation")
    created: int = Field(..., description="Creation timestamp")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Metadata")
    payment_method: Optional[str] = Field(None, description="Payment method ID")
    receipt_email: Optional[str] = Field(None, description="Receipt email")
    latest_charge: Optional[str] = Field(None, description="Latest charge ID")


class StripeWebhookEvent(BaseModel):
    """Stripe webhook event data."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str = Field(..., description="Event ID")
    object: str = Field(..., description="Object type")
    api_version: str = Field(..., description="API version")
    created: int = Field(..., description="Creation timestamp")
    type: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    livemode: bool = Field(..., description="Live mode flag")
    pending_webhooks: int = Field(..., description="Pending webhooks count")
    request: Optional[Dict[str, Any]] = Field(None, description="Request info")


class StripeCharge(BaseModel):
    """Stripe charge object."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str = Field(..., description="Charge ID")
    object: str = Field(..., description="Object type")
    amount: int = Field(..., description="Amount charged")
    currency: str = Field(..., description="Currency code")
    status: str = Field(..., description="Charge status")
    created: int = Field(..., description="Creation timestamp")
    description: Optional[str] = Field(None, description="Charge description")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Metadata")
    payment_intent: Optional[str] = Field(None, description="PaymentIntent ID")
    receipt_email: Optional[str] = Field(None, description="Receipt email")
    receipt_url: Optional[str] = Field(None, description="Receipt URL")


class StripeCustomer(BaseModel):
    """Stripe customer object."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str = Field(..., description="Customer ID")
    object: str = Field(..., description="Object type")
    created: int = Field(..., description="Creation timestamp")
    email: Optional[str] = Field(None, description="Customer email")
    name: Optional[str] = Field(None, description="Customer name")
    phone: Optional[str] = Field(None, description="Customer phone")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Metadata")


class StripeError(BaseModel):
    """Stripe error response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    type: str = Field(..., description="Error type")
    code: Optional[str] = Field(None, description="Error code")
    message: str = Field(..., description="Error message")
    param: Optional[str] = Field(None, description="Parameter causing error")
    decline_code: Optional[str] = Field(None, description="Decline code")


class StripeErrorResponse(BaseModel):
    """Stripe error response wrapper."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    error: StripeError = Field(..., description="Error details")


class StripeCurrenciesResponse(BaseModel):
    """Stripe supported currencies response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies: List[StripeCurrency] = Field(..., description="List of supported currencies")


class StripeWebhookEndpoint(BaseModel):
    """Stripe webhook endpoint configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    id: str = Field(..., description="Webhook endpoint ID")
    object: str = Field(..., description="Object type")
    api_version: Optional[str] = Field(None, description="API version")
    created: int = Field(..., description="Creation timestamp")
    enabled_events: List[str] = Field(..., description="Enabled event types")
    livemode: bool = Field(..., description="Live mode flag")
    status: str = Field(..., description="Endpoint status")
    url: str = Field(..., description="Endpoint URL")


# =============================================================================
# MONITORING & HEALTH CHECK MODELS
# =============================================================================

class StripeHealthErrorResponse(BaseModel):
    """Stripe API error response schema for health checks."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    class StripeHealthError(BaseModel):
        message: str = Field(..., description="Error message")
        type: str = Field(..., description="Error type")
        
    error: StripeHealthError = Field(..., description="Error details")
    
    @field_validator('error')
    @classmethod
    def validate_auth_error(cls, v):
        """Validate this is an authentication error (meaning API is healthy)."""
        if v.type != 'invalid_request_error':
            raise ValueError(f"Expected auth error, got '{v.type}'")
        return v
