from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
from decimal import Decimal

from ...internal_types import ProviderConfig
from .config import PUBLIC_KEY

class CryptAPIConfig(ProviderConfig):
    """CryptAPI provider configuration with Pydantic v2."""
    
    own_address: str = Field(..., description="Your cryptocurrency address")
    callback_url: Optional[str] = Field(default=None, description="Webhook callback URL")
    convert_payments: bool = Field(default=True, description="Auto-convert payments")
    multi_token: bool = Field(default=True, description="Support multi-token payments")
    priority: str = Field(default='default', description="Transaction priority")
    verify_signatures: bool = Field(default=True, description="Enable webhook signature verification")
    
    # CryptAPI's official public key for signature verification
    public_key: str = Field(
        default=PUBLIC_KEY,
        description="CryptAPI RSA public key for signature verification"
    )


class CryptAPICurrency(BaseModel):
    """CryptAPI specific currency model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency_code: str = Field(..., description="Currency symbol (e.g., BTC, ETH)")
    name: str = Field(..., description="Full currency name")
    minimum_transaction: Optional[Decimal] = Field(None, description="Minimum transaction amount")
    maximum_transaction: Optional[Decimal] = Field(None, description="Maximum transaction amount")
    fee_percent: Optional[Decimal] = Field(None, description="Fee percentage")
    logo: Optional[str] = Field(None, description="Currency logo URL")


class CryptAPINetwork(BaseModel):
    """CryptAPI specific network model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currency: str = Field(..., description="Currency code this network belongs to")
    network: str = Field(..., description="Network code (e.g., mainnet, testnet)")
    name: str = Field(..., description="Network display name")
    confirmations: int = Field(1, description="Required confirmations")
    fee: Optional[Decimal] = Field(None, description="Network fee")


class CryptAPIPaymentRequest(BaseModel):
    """CryptAPI payment creation request."""
    ticker: str = Field(..., description="Currency ticker")
    callback: str = Field(..., description="Callback URL")
    address: Optional[str] = Field(None, description="Destination address")
    pending: bool = Field(False, description="Accept pending transactions")
    confirmations: int = Field(1, description="Required confirmations")
    email: Optional[str] = Field(None, description="Email for notifications")
    post: int = Field(0, description="POST data format")
    json: int = Field(1, description="JSON response format")
    priority: Optional[str] = Field(None, description="Priority level")
    multi_token: bool = Field(False, description="Multi-token support")
    convert: int = Field(1, description="Convert amounts")


class CryptAPIPaymentResponse(BaseModel):
    """CryptAPI payment creation response."""
    address_in: str = Field(..., description="Payment address")
    address_out: Optional[str] = Field(None, description="Destination address")
    callback_url: str = Field(..., description="Callback URL")
    priority: Optional[str] = Field(None, description="Priority level")
    minimum: Optional[Decimal] = Field(None, description="Minimum amount")


class CryptAPICallback(BaseModel):
    """CryptAPI webhook callback data according to official documentation."""
    model_config = ConfigDict(validate_assignment=True, extra="allow")  # Allow extra fields for custom params
    
    # Required fields from documentation
    uuid: Optional[str] = Field(None, description="Unique identifier for each payment transaction")
    address_in: str = Field(..., description="CryptAPI-generated payment address")
    address_out: str = Field(..., description="Your destination address(es)")
    txid_in: str = Field(..., description="Transaction hash of customer's payment")
    coin: str = Field(..., description="Cryptocurrency ticker")
    price: Optional[Decimal] = Field(None, description="Cryptocurrency price in USD")
    pending: Optional[int] = Field(0, description="1=pending webhook, 0=confirmed webhook")
    
    # Confirmed webhook only fields
    txid_out: Optional[str] = Field(None, description="CryptAPI's forwarding transaction hash")
    confirmations: Optional[int] = Field(None, description="Number of blockchain confirmations")
    value_coin: Optional[Decimal] = Field(None, description="Payment amount before fees")
    value_forwarded_coin: Optional[Decimal] = Field(None, description="Amount forwarded after fees")
    fee_coin: Optional[Decimal] = Field(None, description="CryptAPI service fee")
    
    # Optional conversion fields (when convert=1)
    value_coin_convert: Optional[str] = Field(None, description="JSON FIAT conversions of value_coin")
    value_forwarded_coin_convert: Optional[str] = Field(None, description="JSON FIAT conversions of value_forwarded_coin")
    
    @field_validator('pending')
    @classmethod
    def validate_pending(cls, v):
        """Validate pending field is 0 or 1."""
        if v not in [0, 1]:
            raise ValueError("pending must be 0 (confirmed) or 1 (pending)")
        return v
    


class CryptAPIInfoResponse(BaseModel):
    """CryptAPI info endpoint response."""
    ticker: str = Field(..., description="Currency ticker")
    minimum_transaction: Decimal = Field(..., description="Minimum transaction amount")
    maximum_transaction: Optional[Decimal] = Field(None, description="Maximum transaction amount")
    fee_percent: Decimal = Field(..., description="Fee percentage")
    network_fee: Decimal = Field(..., description="Network fee")
    prices: Dict[str, Decimal] = Field(..., description="Price conversions")


class CryptAPIEstimateFeeResponse(BaseModel):
    """CryptAPI fee estimation response."""
    estimated_cost: Decimal = Field(..., description="Estimated cost")
    estimated_cost_currency: Dict[str, Decimal] = Field(..., description="Cost in different currencies")


class CryptAPIConvertResponse(BaseModel):
    """CryptAPI currency conversion response."""
    value_coin: Decimal = Field(..., description="Value in cryptocurrency")
    exchange_rate: Decimal = Field(..., description="Exchange rate used")


class CryptAPIQRCodeResponse(BaseModel):
    """CryptAPI QR code response."""
    qr_code: str = Field(..., description="Base64 encoded QR code image")
    payment_uri: str = Field(..., description="Payment URI for QR code")


class CryptAPILogsResponse(BaseModel):
    """CryptAPI logs response."""
    callbacks: List[Dict[str, Any]] = Field(default_factory=list, description="Callback logs")
    payments: List[Dict[str, Any]] = Field(default_factory=list, description="Payment logs")


class CryptAPISupportedCoinsResponse(BaseModel):
    """CryptAPI supported coins response."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies: List[CryptAPICurrency] = Field(..., description="List of supported currencies")


# =============================================================================
# MONITORING & HEALTH CHECK MODELS
# =============================================================================

class CryptAPIInfoResponse(BaseModel):
    """CryptAPI /btc/info/ response schema for health checks."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    coin: str = Field(..., description="Cryptocurrency name")
    logo: str = Field(..., description="Logo URL")
    ticker: str = Field(..., description="Currency ticker")
    minimum_transaction: int = Field(..., description="Minimum transaction in satoshis")
    minimum_transaction_coin: str = Field(..., description="Minimum transaction in coin units")
    minimum_fee: int = Field(..., description="Minimum fee in satoshis")
    minimum_fee_coin: str = Field(..., description="Minimum fee in coin units")
    fee_percent: str = Field(..., description="Fee percentage")
    network_fee_estimation: str = Field(..., description="Network fee estimation")
    status: str = Field(..., description="API status")
    prices: Dict[str, str] = Field(..., description="Prices in various fiat currencies")
    prices_updated: str = Field(..., description="Prices last updated timestamp")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate that status is success."""
        if v != 'success':
            raise ValueError(f"Expected status 'success', got '{v}'")
        return v
    
    @field_validator('prices')
    @classmethod
    def validate_prices_not_empty(cls, v):
        """Validate that prices dict is not empty."""
        if not v:
            raise ValueError("Prices dictionary cannot be empty")
        return v
    
    def get_usd_price(self) -> Optional[Decimal]:
        """Get USD price as Decimal."""
        usd_price = self.prices.get('USD')
        if usd_price:
            try:
                return Decimal(usd_price)
            except:
                return None
        return None
