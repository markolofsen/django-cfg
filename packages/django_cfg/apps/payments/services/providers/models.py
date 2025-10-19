"""
Pydantic models for provider layer (Payments v2.0).

Used for validation between Service Layer and Provider Layer.
"""

from decimal import Decimal
from typing import Any, Dict, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaymentRequest(BaseModel):
    """
    Request for creating a payment.
    Used between Service → Provider.
    """

    amount_usd: Decimal = Field(ge=Decimal('1.0'), le=Decimal('50000.0'), description="Amount in USD")
    currency_code: str = Field(min_length=3, max_length=20, description="Currency code (e.g., USDTTRC20)")
    order_id: str = Field(min_length=10, max_length=100, description="Internal payment ID")
    description: Optional[str] = Field(None, max_length=500, description="Payment description")

    model_config = ConfigDict(frozen=True)  # immutable

    @field_validator('currency_code')
    @classmethod
    def validate_currency_code(cls, v):
        """Ensure currency code is uppercase."""
        return v.upper()


class ProviderResponse(BaseModel):
    """
    Response from provider.
    Universal model for all providers.
    """

    success: bool = Field(description="Whether the operation was successful")
    provider_payment_id: Optional[str] = Field(None, description="Provider's payment ID")
    status: Optional[str] = Field(None, description="Payment status from provider")
    wallet_address: Optional[str] = Field(None, description="Payment wallet address")
    amount: Optional[Decimal] = Field(None, description="Amount to pay in crypto")
    actual_amount: Optional[Decimal] = Field(None, description="Actually received amount")
    currency: Optional[str] = Field(None, description="Currency code")
    transaction_hash: Optional[str] = Field(None, description="Blockchain transaction hash")
    payment_url: Optional[str] = Field(None, description="Payment page URL")
    expires_at: Optional[datetime] = Field(None, description="Payment expiration time")
    confirmations_count: int = Field(default=0, description="Number of confirmations")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    raw_response: Dict[str, Any] = Field(default_factory=dict, description="Raw provider response")

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'success': True,
                'provider_payment_id': '123456',
                'status': 'pending',
                'wallet_address': 'TXYZabc123...',
                'amount': '100.234567',
                'currency': 'USDTTRC20'
            }
        }
    )


class CurrencyInfo(BaseModel):
    """
    Currency information from provider.
    Used for currency synchronization.
    """

    code: str = Field(description="Provider currency code (e.g., USDTTRC20)")
    name: str = Field(description="Full currency name")
    token: str = Field(description="Token symbol (e.g., USDT)")
    network: Optional[str] = Field(None, description="Network name (e.g., TRC20)")
    is_enabled: bool = Field(default=True, description="Is currency enabled")
    is_popular: bool = Field(default=False, description="Is popular currency")
    is_stable: bool = Field(default=False, description="Is stablecoin")
    logo_url: Optional[str] = Field(None, description="Currency logo URL")
    min_amount_usd: Decimal = Field(default=Decimal('1.0'), description="Minimum amount in USD")
    priority: int = Field(default=0, description="Display priority (lower = higher)")

    model_config = ConfigDict(frozen=True)
