"""
Base provider models for Universal Payment System v2.0.

Core Pydantic models for provider configuration and requests.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ProviderType(str, Enum):
    """Provider type classification."""
    
    CRYPTO = "crypto"
    FIAT = "fiat"
    HYBRID = "hybrid"  # Supports both fiat and crypto


class ProviderStatus(str, Enum):
    """Provider operational status."""
    
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


class ProviderConfig(BaseModel):
    """
    Base provider configuration with Pydantic v2.
    
    Common configuration fields for all payment providers.
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        frozen=False
    )
    
    provider_name: str = Field(..., description="Provider name")
    api_key: str = Field(..., description="Provider API key")
    api_url: str = Field(..., description="Provider API URL")
    enabled: bool = Field(default=True, description="Whether provider is enabled")
    sandbox_mode: bool = Field(default=False, description="Sandbox mode")
    timeout: int = Field(default=30, ge=5, le=300, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    retry_delay: int = Field(default=5, ge=1, le=60, description="Delay between retries in seconds")
    min_amount_usd: float = Field(default=1.0, ge=0.01, description="Minimum amount in USD")
    max_amount_usd: float = Field(default=50000.0, ge=1.0, description="Maximum amount in USD")
    supported_currencies: List[str] = Field(default_factory=list, description="Supported currencies")
    webhook_secret: Optional[str] = Field(None, description="Webhook secret for validation")


class PaymentRequest(BaseModel):
    """
    Universal payment request for providers with Pydantic v2.
    
    Standardized payment creation request across all providers.
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True
    )
    
    amount_usd: float = Field(..., gt=0, description="Amount in USD")
    currency_code: str = Field(..., min_length=3, max_length=10, description="Currency code")
    order_id: str = Field(..., min_length=1, max_length=100, description="Internal order/payment ID")
    callback_url: Optional[str] = Field(None, description="Success callback URL")
    cancel_url: Optional[str] = Field(None, description="Cancel URL")
    description: Optional[str] = Field(None, max_length=500, description="Payment description")
    customer_email: Optional[str] = Field(None, description="Customer email")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class WithdrawalRequest(BaseModel):
    """
    Universal withdrawal request for providers with Pydantic v2.
    
    Standardized withdrawal/payout request across all providers.
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True
    )
    
    amount: float = Field(..., gt=0, description="Withdrawal amount in crypto currency")
    currency_code: str = Field(..., min_length=3, max_length=10, description="Cryptocurrency code")
    destination_address: str = Field(..., min_length=10, description="Destination wallet address")
    withdrawal_id: str = Field(..., min_length=1, max_length=100, description="Internal withdrawal ID")
    callback_url: Optional[str] = Field(None, description="Withdrawal status callback URL")
    description: Optional[str] = Field(None, max_length=500, description="Withdrawal description")
    extra_id: Optional[str] = Field(None, description="Extra ID for destination (memo, tag, etc.)")
    priority: Optional[str] = Field(default="normal", description="Transaction priority (low, normal, high)")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProviderMetadata(BaseModel):
    """
    Provider metadata with classification and features.
    
    Contains provider-specific information for routing and display.
    """
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=True  # Metadata should be immutable
    )
    
    name: str = Field(..., description="Human-readable provider name")
    provider_type: ProviderType = Field(..., description="Provider type (crypto/fiat/hybrid)")
    status: ProviderStatus = Field(default=ProviderStatus.ACTIVE, description="Provider status")
    priority: int = Field(default=100, ge=0, le=1000, description="Provider priority (lower = higher priority)")
    
    # Feature flags
    supports_fiat: bool = Field(default=False, description="Supports fiat currencies")
    supports_crypto: bool = Field(default=True, description="Supports cryptocurrencies")
    supports_webhooks: bool = Field(default=True, description="Supports webhook notifications")
    supports_refunds: bool = Field(default=False, description="Supports payment refunds")
    supports_partial_payments: bool = Field(default=False, description="Supports partial payments")
    
    # Limits and fees
    min_amount_usd: float = Field(default=1.0, ge=0.01, description="Minimum payment amount in USD")
    max_amount_usd: float = Field(default=50000.0, ge=1.0, description="Maximum payment amount in USD")
    fee_percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Fee percentage")
    fixed_fee_usd: float = Field(default=0.0, ge=0.0, description="Fixed fee in USD")
    
    # Geographic and regulatory
    supported_countries: List[str] = Field(default_factory=list, description="Supported country codes")
    restricted_countries: List[str] = Field(default_factory=list, description="Restricted country codes")
    requires_kyc: bool = Field(default=False, description="Requires KYC verification")
    
    # Technical details
    api_version: str = Field(default="v1", description="API version")
    documentation_url: Optional[str] = Field(None, description="API documentation URL")
    status_page_url: Optional[str] = Field(None, description="Provider status page URL")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list, description="Provider tags for categorization")
    description: Optional[str] = Field(None, max_length=500, description="Provider description")
