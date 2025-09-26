"""
Data types for the Universal Payment System v2.0.

Pydantic models for internal data representation and transfer.
"""

from decimal import Decimal
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class PaymentData(BaseModel):
    """Internal payment data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    id: str = Field(description="Payment ID")
    user_id: int = Field(description="User ID")
    amount_usd: float = Field(description="Amount in USD")
    crypto_amount: Optional[Decimal] = Field(None, description="Cryptocurrency amount")
    currency_code: str = Field(description="Cryptocurrency code")
    provider: str = Field(description="Payment provider")
    status: str = Field(description="Payment status")
    provider_payment_id: Optional[str] = Field(None, description="Provider payment ID")
    payment_url: Optional[str] = Field(None, description="Payment URL")
    qr_code_url: Optional[str] = Field(None, description="QR code URL")
    wallet_address: Optional[str] = Field(None, description="Wallet address")
    callback_url: Optional[str] = Field(None, description="Success callback URL")
    cancel_url: Optional[str] = Field(None, description="Cancel URL")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Payment expiration")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class BalanceData(BaseModel):
    """Internal balance data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    user_id: int = Field(description="User ID")
    balance_usd: float = Field(description="Balance in USD")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class TransactionData(BaseModel):
    """Internal transaction data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    id: str = Field(description="Transaction ID")
    user_id: int = Field(description="User ID")
    amount: float = Field(description="Transaction amount")
    transaction_type: str = Field(description="Transaction type")
    description: Optional[str] = Field(None, description="Transaction description")
    payment_id: Optional[str] = Field(None, description="Related payment ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Creation timestamp")


class SubscriptionData(BaseModel):
    """Internal subscription data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    id: str = Field(description="Subscription ID")
    user_id: int = Field(description="User ID")
    tier: str = Field(description="Subscription tier")
    status: str = Field(description="Subscription status")
    requests_per_hour: int = Field(description="Requests per hour limit")
    requests_per_day: int = Field(description="Requests per day limit")
    total_requests: int = Field(default=0, description="Total requests made")
    monthly_cost_usd: float = Field(description="Monthly cost in USD")
    auto_renew: bool = Field(default=False, description="Auto-renewal enabled")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Subscription expiration")
    last_request_at: Optional[datetime] = Field(None, description="Last request timestamp")
    endpoint_groups: List[str] = Field(default_factory=list, description="Allowed endpoint groups")


class CurrencyData(BaseModel):
    """Internal currency data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    code: str = Field(description="Currency code")
    name: str = Field(description="Currency name")
    currency_type: str = Field(description="Currency type (fiat/crypto)")
    symbol: Optional[str] = Field(None, description="Currency symbol")
    decimal_places: int = Field(default=8, description="Decimal places")
    is_enabled: bool = Field(default=True, description="Currency enabled status")
    min_amount: Optional[Decimal] = Field(None, description="Minimum amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum amount")
    network_fee: Optional[Decimal] = Field(None, description="Network fee")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class ProviderData(BaseModel):
    """Internal provider data representation."""
    model_config = ConfigDict(validate_assignment=True)
    
    name: str = Field(description="Provider name")
    display_name: str = Field(description="Provider display name")
    is_enabled: bool = Field(default=True, description="Provider enabled status")
    api_url: str = Field(description="Provider API URL")
    supported_currencies: List[str] = Field(default_factory=list, description="Supported currencies")
    min_amount_usd: float = Field(default=1.0, description="Minimum amount in USD")
    max_amount_usd: float = Field(default=50000.0, description="Maximum amount in USD")
    fee_percentage: float = Field(default=0.0, description="Provider fee percentage")
    confirmation_blocks: Dict[str, int] = Field(default_factory=dict, description="Confirmation blocks per currency")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    is_healthy: bool = Field(default=True, description="Provider health status")
    last_health_check: Optional[datetime] = Field(None, description="Last health check")
    response_time_ms: Optional[int] = Field(None, description="Average response time")


class APIKeyData(BaseModel):
    """Internal API key data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    id: str = Field(description="API key ID")
    user_id: int = Field(description="User ID")
    name: str = Field(description="API key name")
    key_prefix: str = Field(description="Key prefix for display")
    is_active: bool = Field(default=True, description="API key active status")
    total_requests: int = Field(default=0, description="Total requests made")
    allowed_ips: Optional[str] = Field(None, description="Allowed IP addresses")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_used_at: Optional[datetime] = Field(None, description="Last used timestamp")


class NetworkData(BaseModel):
    """Internal network data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    code: str = Field(description="Network code")
    name: str = Field(description="Network name")
    currency_code: str = Field(description="Base currency code")
    is_testnet: bool = Field(default=False, description="Is testnet")
    confirmation_blocks: int = Field(default=1, description="Required confirmation blocks")
    block_time_seconds: int = Field(default=600, description="Average block time")
    is_enabled: bool = Field(default=True, description="Network enabled status")


class TariffData(BaseModel):
    """Internal tariff data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    id: str = Field(description="Tariff ID")
    name: str = Field(description="Tariff name")
    tier: str = Field(description="Subscription tier")
    monthly_price_usd: float = Field(description="Monthly price in USD")
    yearly_price_usd: Optional[float] = Field(None, description="Yearly price in USD")
    requests_per_hour: int = Field(description="Requests per hour limit")
    requests_per_day: int = Field(description="Requests per day limit")
    features: List[str] = Field(default_factory=list, description="Included features")
    is_active: bool = Field(default=True, description="Tariff active status")
    sort_order: int = Field(default=0, description="Display sort order")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class EndpointGroupData(BaseModel):
    """Internal endpoint group data representation."""
    model_config = ConfigDict(validate_assignment=True, from_attributes=True)
    
    code: str = Field(description="Endpoint group code")
    name: str = Field(description="Endpoint group name")
    description: Optional[str] = Field(None, description="Group description")
    rate_limit_per_hour: Optional[int] = Field(None, description="Rate limit per hour")
    is_enabled: bool = Field(default=True, description="Group enabled status")
    endpoints: List[str] = Field(default_factory=list, description="Included endpoints")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
