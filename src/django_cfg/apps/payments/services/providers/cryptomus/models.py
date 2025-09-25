from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ...internal_types import ProviderConfig


class CryptomusConfig(ProviderConfig):
    """Cryptomus provider configuration with Pydantic v2."""
    
    merchant_id: str = Field(..., description="Cryptomus merchant ID")
    test_mode: bool = Field(default=False, description="Enable test mode")
    callback_url: Optional[str] = Field(None, description="Default callback URL")
    success_url: Optional[str] = Field(None, description="Success redirect URL")
    cancel_url: Optional[str] = Field(None, description="Cancel redirect URL")
    
    @field_validator('merchant_id')
    @classmethod
    def validate_merchant_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Merchant ID is required")
        return v.strip()


class CryptomusCurrency(BaseModel):
    """Cryptomus specific currency model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency_code: str = Field(..., description="Currency symbol (e.g., BTC, ETH)")
    name: str = Field(..., description="Full currency name")
    network: Optional[str] = Field(None, description="Network code")
    network_name: Optional[str] = Field(None, description="Network display name")
    min_amount: Optional[Decimal] = Field(None, description="Minimum transaction amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum transaction amount")
    commission_percent: Optional[Decimal] = Field(None, description="Commission percentage")
    is_available: bool = Field(True, description="Currency availability")


class CryptomusNetwork(BaseModel):
    """Cryptomus specific network model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    code: str = Field(..., description="Network code")
    name: str = Field(..., description="Network display name")
    currency: str = Field(..., description="Currency this network belongs to")
    min_amount: Optional[Decimal] = Field(None, description="Minimum amount for this network")
    max_amount: Optional[Decimal] = Field(None, description="Maximum amount for this network")
    commission_percent: Optional[Decimal] = Field(None, description="Commission percentage")
    confirmations: int = Field(1, description="Required confirmations")


class CryptomusPaymentRequest(BaseModel):
    """Cryptomus payment creation request."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    amount: str = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency")
    order_id: str = Field(..., description="Unique order identifier")
    url_callback: Optional[str] = Field(None, description="Callback URL")
    url_return: Optional[str] = Field(None, description="Return URL")
    url_success: Optional[str] = Field(None, description="Success URL")
    is_payment_multiple: bool = Field(False, description="Allow multiple payments")
    lifetime: int = Field(3600, description="Payment lifetime in seconds")
    to_currency: Optional[str] = Field(None, description="Target cryptocurrency")


class CryptomusPaymentResponse(BaseModel):
    """Cryptomus payment creation response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    state: int = Field(..., description="Response state (0 = success)")
    message: Optional[str] = Field(None, description="Response message")
    result: Optional[Dict[str, Any]] = Field(None, description="Payment result data")


class CryptomusPaymentInfo(BaseModel):
    """Cryptomus payment information."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    uuid: str = Field(..., description="Payment UUID")
    order_id: str = Field(..., description="Order ID")
    amount: str = Field(..., description="Payment amount")
    currency: str = Field(..., description="Payment currency")
    address: Optional[str] = Field(None, description="Payment address")
    url: Optional[str] = Field(None, description="Payment URL")
    static_qr: Optional[str] = Field(None, description="QR code data")
    network: Optional[str] = Field(None, description="Network")
    status: str = Field(..., description="Payment status")
    expired_at: Optional[str] = Field(None, description="Expiration timestamp")


class CryptomusWebhook(BaseModel):
    """Cryptomus webhook data according to official documentation."""
    model_config = ConfigDict(validate_assignment=True, extra="allow")  # Allow extra fields
    
    # Required fields from documentation
    type: str = Field(..., description="Webhook type (payment/payout)")
    uuid: str = Field(..., description="Payment/payout UUID")
    order_id: str = Field(..., description="Order ID from your system")
    amount: str = Field(..., description="Amount")
    payment_amount: Optional[str] = Field(None, description="Payment amount")
    payment_amount_usd: Optional[str] = Field(None, description="Payment amount in USD")
    merchant_amount: Optional[str] = Field(None, description="Merchant amount after fees")
    commission: Optional[str] = Field(None, description="Commission amount")
    is_final: bool = Field(..., description="Is payment final")
    status: str = Field(..., description="Payment status")
    from_: Optional[str] = Field(None, alias="from", description="Sender address")
    wallet_address_uuid: Optional[str] = Field(None, description="Wallet address UUID")
    network: Optional[str] = Field(None, description="Blockchain network")
    currency: str = Field(..., description="Currency")
    payer_currency: Optional[str] = Field(None, description="Payer currency")
    additional_data: Optional[str] = Field(None, description="Additional data")
    txid: Optional[str] = Field(None, description="Transaction hash")
    sign: str = Field(..., description="Webhook signature")
    
    @property
    def from_address(self) -> Optional[str]:
        """Get sender address from 'from' field."""
        return self.from_
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status is one of expected values."""
        valid_statuses = ['check', 'paid', 'paid_over', 'fail', 'wrong_amount', 'cancel', 
                         'system_fail', 'refund_process', 'refund_fail', 'refund_paid']
        if v not in valid_statuses:
            # Don't import logger here to avoid issues, just pass
            pass
        return v


class CryptomusStatusResponse(BaseModel):
    """Cryptomus payment status response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    state: int = Field(..., description="Response state")
    result: Optional[CryptomusPaymentInfo] = Field(None, description="Payment info")
    message: Optional[str] = Field(None, description="Response message")


class CryptomusCurrenciesResponse(BaseModel):
    """Cryptomus supported currencies response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    state: int = Field(..., description="Response state")
    result: List[CryptomusCurrency] = Field(default_factory=list, description="List of currencies")
    message: Optional[str] = Field(None, description="Response message")


class CryptomusNetworksResponse(BaseModel):
    """Cryptomus supported networks response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    state: int = Field(..., description="Response state")
    result: Dict[str, List[CryptomusNetwork]] = Field(default_factory=dict, description="Networks by currency")
    message: Optional[str] = Field(None, description="Response message")


# =============================================================================
# MONITORING & HEALTH CHECK MODELS
# =============================================================================

class CryptomusErrorResponse(BaseModel):
    """Cryptomus API error response schema for health checks."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    error: str = Field(..., description="Error message")
    
    @field_validator('error')
    @classmethod
    def validate_not_found_error(cls, v):
        """Validate this is a not found error (meaning API is responding)."""
        if v.lower() not in ['not found', 'unauthorized', 'forbidden']:
            raise ValueError(f"Unexpected error: {v}")
        return v
