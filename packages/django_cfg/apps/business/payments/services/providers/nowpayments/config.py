"""
NowPayments provider configuration for Payments v2.0.

Simple configuration constants and Pydantic config model.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, SecretStr, field_validator


# Configuration constants
class NowPaymentsConstants:
    """NowPayments configuration constants."""

    # API URLs
    PRODUCTION_API_URL = "https://api.nowpayments.io/v1/"
    SANDBOX_API_URL = "https://api-sandbox.nowpayments.io/v1/"

    # Fees
    FEE_PERCENTAGE = Decimal('0.005')  # 0.5%
    FIXED_FEE_USD = Decimal('0.0')     # No fixed fee

    # Limits
    MIN_AMOUNT_USD = Decimal('1.0')
    MAX_AMOUNT_USD = Decimal('50000.0')

    # Expiration
    PAYMENT_EXPIRATION_MINUTES = 30

    # Network names for display
    NETWORK_NAMES = {
        'eth': 'Ethereum',
        'erc20': 'ERC20',
        'bsc': 'Binance Smart Chain',
        'matic': 'Polygon',
        'trx': 'TRON',
        'trc20': 'TRC20',
        'btc': 'Bitcoin',
        'ltc': 'Litecoin',
        'sol': 'Solana',
        'avaxc': 'Avalanche C-Chain',
        'arbitrum': 'Arbitrum',
        'op': 'Optimism',
        'base': 'Base',
    }

    # Confirmation blocks required
    CONFIRMATION_BLOCKS = {
        'btc': 1,
        'eth': 12,
        'erc20': 12,
        'bsc': 3,
        'matic': 20,
        'trx': 19,
        'trc20': 19,
    }


class NowPaymentsConfig(BaseModel):
    """
    NowPayments provider configuration.
    Immutable, validated on creation.
    """

    api_key: SecretStr = Field(description="NowPayments API key")
    api_url: HttpUrl = Field(
        default=NowPaymentsConstants.PRODUCTION_API_URL,
        description="Base API URL"
    )
    sandbox: bool = Field(default=False, description="Use sandbox mode")
    timeout: int = Field(default=30, ge=5, le=120, description="Request timeout in seconds")

    # Limits (from constants)
    min_amount_usd: Decimal = Field(
        default=NowPaymentsConstants.MIN_AMOUNT_USD,
        ge=Decimal('0.01')
    )
    max_amount_usd: Decimal = Field(
        default=NowPaymentsConstants.MAX_AMOUNT_USD
    )

    # Expiration
    payment_expiration_minutes: int = Field(
        default=NowPaymentsConstants.PAYMENT_EXPIRATION_MINUTES,
        ge=10,
        le=120
    )

    model_config = ConfigDict(
        frozen=True,  # immutable
        validate_assignment=True,
        str_strip_whitespace=True,
        extra='forbid'  # forbid extra fields
    )

    @field_validator('api_url')
    @classmethod
    def validate_api_url(cls, v):
        """Ensure URL ends with slash."""
        url_str = str(v)
        if not url_str.endswith('/'):
            url_str += '/'
        return url_str

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.sandbox

    @property
    def api_key_str(self) -> str:
        """Get API key as string."""
        return self.api_key.get_secret_value()

    @classmethod
    def get_network_name(cls, network_code: str) -> str:
        """Get human-readable network name."""
        if not network_code:
            return ""
        return NowPaymentsConstants.NETWORK_NAMES.get(
            network_code.lower(),
            network_code.upper()
        )

    @classmethod
    def get_confirmation_blocks(cls, network_code: str) -> int:
        """Get confirmation blocks for network."""
        if not network_code:
            return 1
        return NowPaymentsConstants.CONFIRMATION_BLOCKS.get(
            network_code.lower(),
            1
        )
