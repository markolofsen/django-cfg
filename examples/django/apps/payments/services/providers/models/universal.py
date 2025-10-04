"""
Universal models for cross-provider compatibility.

These models provide a standardized interface across different payment providers.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class UniversalCurrency(BaseModel):
    """Universal currency representation for cross-provider compatibility."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider_currency_code: str = Field(..., description="Provider-specific currency code")
    base_currency_code: str = Field(..., description="Base currency code (e.g., BTC, USDT)")
    network_code: Optional[str] = Field(None, description="Network code (e.g., eth, bsc, tron)")
    name: str = Field(..., description="Human-readable currency name")
    currency_type: str = Field(..., description="Currency type (fiat, crypto, metal)")
    is_enabled: bool = Field(default=True, description="Whether currency is enabled")
    is_popular: bool = Field(default=False, description="Whether currency is popular")
    is_stable: bool = Field(default=False, description="Whether currency is a stablecoin")
    priority: int = Field(default=0, description="Currency priority for sorting")
    logo_url: str = Field(default="", description="Currency logo URL")
    available_for_payment: bool = Field(default=True, description="Available for payment")
    available_for_payout: bool = Field(default=True, description="Available for payout")
    min_payment_amount: Optional[float] = Field(None, description="Minimum payment amount in USD")
    raw_data: dict = Field(default_factory=dict, description="Raw provider data")


class UniversalCurrenciesResponse(BaseModel):
    """Response containing list of universal currencies."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies: List[UniversalCurrency] = Field(default_factory=list, description="List of currencies")


class CurrencySyncResult(BaseModel):
    """Result of currency synchronization operation."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    currencies_created: int = Field(default=0, description="Number of currencies created")
    currencies_updated: int = Field(default=0, description="Number of currencies updated")
    networks_created: int = Field(default=0, description="Number of networks created")
    provider_currencies_created: int = Field(default=0, description="Number of provider currencies created")
    provider_currencies_updated: int = Field(default=0, description="Number of provider currencies updated")
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    total_processed: int = Field(default=0, description="Total currencies processed")
