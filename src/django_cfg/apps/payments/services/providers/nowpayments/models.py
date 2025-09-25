from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from decimal import Decimal

from ...internal_types import ProviderConfig


class NowPaymentsConfig(ProviderConfig):
    """NowPayments provider configuration with Pydantic v2."""
    
    ipn_secret: Optional[str] = Field(default=None, description="IPN secret for webhook validation")
    callback_url: Optional[str] = Field(default=None, description="Webhook callback URL")
    success_url: Optional[str] = Field(default=None, description="Payment success redirect URL")
    cancel_url: Optional[str] = Field(default=None, description="Payment cancel redirect URL")
    
    


class NowPaymentsCurrency(BaseModel):
    """NowPayments full currency model from /v1/full-currencies."""
    model_config = ConfigDict(validate_assignment=True, extra="allow")
    
    id: int = Field(..., description="Currency ID")
    code: str = Field(..., description="Currency code (e.g., BTC, USDTERC20)")
    name: str = Field(..., description="Full currency name")
    enable: bool = Field(..., description="Currency availability")
    wallet_regex: Optional[str] = Field(None, description="Wallet address regex")
    priority: int = Field(..., description="Currency priority")
    extra_id_exists: bool = Field(..., description="Whether extra ID is required")
    extra_id_regex: Optional[str] = Field(None, description="Extra ID regex")
    logo_url: str = Field(..., description="Currency logo URL")
    track: bool = Field(..., description="Track transactions")
    cg_id: Optional[str] = Field(None, description="CoinGecko ID")
    is_maxlimit: bool = Field(..., description="Has max limit")
    network: Optional[str] = Field(None, description="Blockchain network")
    smart_contract: Optional[str] = Field(None, description="Smart contract address")
    network_precision: Optional[str] = Field(None, description="Network precision")
    explorer_link_hash: Optional[str] = Field(None, description="Explorer link")
    precision: int = Field(..., description="Currency precision")
    ticker: Optional[str] = Field(None, description="Ticker symbol")
    is_defi: bool = Field(..., description="Is DeFi token")
    is_popular: bool = Field(..., description="Is popular currency")
    is_stable: bool = Field(..., description="Is stablecoin")
    available_for_to_conversion: bool = Field(..., description="Available for conversion")
    trust_wallet_id: Optional[str] = Field(None, description="Trust Wallet ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")
    available_for_payment: bool = Field(..., description="Available for payment")
    available_for_payout: bool = Field(..., description="Available for payout")
    extra_id_optional: bool = Field(..., description="Extra ID is optional")


class NowPaymentsNetwork(BaseModel):
    """NowPayments specific network model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    code: str = Field(..., description="Network code")
    name: str = Field(..., description="Network display name")
    currency: str = Field(..., description="Currency this network belongs to")
    confirmations: int = Field(1, description="Required confirmations")


class NowPaymentsPaymentRequest(BaseModel):
    """NowPayments payment creation request."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    price_amount: float = Field(..., description="Payment amount")
    price_currency: str = Field(..., description="Price currency (usually USD)")
    pay_currency: str = Field(..., description="Payment currency (crypto)")
    order_id: str = Field(..., description="Unique order identifier")
    order_description: Optional[str] = Field(None, description="Order description")
    success_url: Optional[str] = Field(None, description="Success redirect URL")
    cancel_url: Optional[str] = Field(None, description="Cancel redirect URL")
    ipn_callback_url: Optional[str] = Field(None, description="IPN callback URL")


class NowPaymentsPaymentResponse(BaseModel):
    """NowPayments payment creation response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    payment_id: str = Field(..., description="Payment ID")
    payment_status: str = Field(..., description="Payment status")
    pay_address: str = Field(..., description="Payment address")
    price_amount: float = Field(..., description="Price amount")
    price_currency: str = Field(..., description="Price currency")
    pay_amount: float = Field(..., description="Payment amount")
    pay_currency: str = Field(..., description="Payment currency")
    order_id: str = Field(..., description="Order ID")
    order_description: Optional[str] = Field(None, description="Order description")
    invoice_url: Optional[str] = Field(None, description="Payment page URL")
    success_url: Optional[str] = Field(None, description="Success URL")
    cancel_url: Optional[str] = Field(None, description="Cancel URL")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")


class NowPaymentsWebhook(BaseModel):
    """NowPayments webhook/IPN data."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    payment_id: str = Field(..., description="Payment ID")
    payment_status: str = Field(..., description="Payment status")
    pay_address: str = Field(..., description="Payment address")
    price_amount: float = Field(..., description="Price amount")
    price_currency: str = Field(..., description="Price currency")
    pay_amount: float = Field(..., description="Payment amount")
    pay_currency: str = Field(..., description="Payment currency")
    order_id: str = Field(..., description="Order ID")
    order_description: Optional[str] = Field(None, description="Order description")
    outcome_amount: Optional[float] = Field(None, description="Outcome amount")
    outcome_currency: Optional[str] = Field(None, description="Outcome currency")
    actually_paid: Optional[float] = Field(None, description="Actually paid amount")
    txid: Optional[str] = Field(None, description="Transaction ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")


class NowPaymentsStatusResponse(BaseModel):
    """NowPayments payment status response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    payment_id: str = Field(..., description="Payment ID")
    payment_status: str = Field(..., description="Payment status")
    pay_address: str = Field(..., description="Payment address")
    price_amount: float = Field(..., description="Price amount")
    price_currency: str = Field(..., description="Price currency")
    pay_amount: float = Field(..., description="Payment amount")
    pay_currency: str = Field(..., description="Payment currency")
    order_id: str = Field(..., description="Order ID")
    order_description: Optional[str] = Field(None, description="Order description")
    outcome_amount: Optional[float] = Field(None, description="Outcome amount")
    outcome_currency: Optional[str] = Field(None, description="Outcome currency")
    actually_paid: Optional[float] = Field(None, description="Actually paid amount")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")


class NowPaymentsCurrenciesResponse(BaseModel):
    """NowPayments supported currencies response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies: List[str] = Field(..., description="List of supported currency codes")


class NowPaymentsFullCurrenciesResponse(BaseModel):
    """NowPayments full currencies response from /v1/full-currencies."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies: List[NowPaymentsCurrency] = Field(..., description="List of full currency data")


class NowPaymentsMinAmountResponse(BaseModel):
    """NowPayments minimum amount response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency_from: str = Field(..., description="Source currency")
    currency_to: str = Field(..., description="Target currency")
    min_amount: float = Field(..., description="Minimum payment amount")


class NowPaymentsEstimateResponse(BaseModel):
    """NowPayments payment estimate response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency_from: str = Field(..., description="Source currency")
    currency_to: str = Field(..., description="Target currency")
    amount_from: float = Field(..., description="Source amount")
    estimated_amount: float = Field(..., description="Estimated target amount")
    fee_amount: Optional[float] = Field(None, description="Fee amount")


class NowPaymentsStatusInfo(BaseModel):
    """NowPayments API status response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    message: str = Field(..., description="Status message")
    uptime: Optional[float] = Field(None, description="API uptime percentage")


# =============================================================================
# MONITORING & HEALTH CHECK MODELS
# =============================================================================

class NowPaymentsStatusResponse(BaseModel):
    """NowPayments /v1/status response schema for health checks."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    message: str = Field(..., description="Status message")
    
    @field_validator('message')
    @classmethod
    def validate_message_ok(cls, v):
        """Validate that message is OK."""
        if v.upper() != 'OK':
            raise ValueError(f"Expected message 'OK', got '{v}'")
        return v
