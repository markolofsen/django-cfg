"""
Provider-specific currency and network models.

These models are ONLY for provider-specific currency data,
NOT for universal service communication (those are in internal_types.py).
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from typing import List, Dict, Optional, Any
from enum import Enum


class CurrencyType(str, Enum):
    """Currency type enumeration."""
    FIAT = "fiat"
    CRYPTO = "crypto"


class NetworkType(str, Enum):
    """Network type enumeration."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    LAYER2 = "layer2"
    SIDECHAIN = "sidechain"


class CurrencyInfo(BaseModel):
    """Information about a currency from provider API."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    code: str = Field(min_length=2, max_length=10, description="Currency code (BTC, ETH, USD)")
    name: str = Field(min_length=1, max_length=100, description="Full currency name")
    symbol: Optional[str] = Field(None, max_length=10, description="Currency symbol")
    currency_type: CurrencyType = Field(description="Type of currency")
    
    # Provider-specific data
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum payment amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum payment amount")
    precision: Optional[int] = Field(None, ge=0, le=18, description="Decimal precision")
    
    # Exchange rate info
    usd_rate: Optional[Decimal] = Field(None, gt=0, description="Rate to USD")
    rate_updated_at: Optional[str] = Field(None, description="Rate update timestamp")
    
    # Provider metadata
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific data")
    
    @field_validator('code')
    @classmethod
    def code_must_be_uppercase(cls, v):
        return v.upper() if v else v
    
    @field_validator('max_amount')
    @classmethod
    def max_amount_must_be_greater_than_min(cls, v, info):
        if v is not None and 'min_amount' in info.data and info.data['min_amount'] is not None:
            if v <= info.data['min_amount']:
                raise ValueError('max_amount must be greater than min_amount')
        return v


class NetworkInfo(BaseModel):
    """Information about a blockchain network from provider API."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    code: str = Field(min_length=1, max_length=20, description="Network code")
    name: str = Field(min_length=1, max_length=50, description="Network display name")
    network_type: Optional[NetworkType] = Field(None, description="Type of network")
    
    # Network-specific settings
    confirmation_blocks: int = Field(default=1, ge=0, description="Required confirmations")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum amount for this network")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum amount for this network")
    
    # Fee information
    base_fee: Optional[Decimal] = Field(None, ge=0, description="Base network fee")
    fee_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Fee percentage")
    
    # Network status
    is_active: bool = Field(default=True, description="Whether network is active")
    is_maintenance: bool = Field(default=False, description="Whether network is in maintenance")
    
    # Provider metadata
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific data")
    
    @field_validator('code')
    @classmethod
    def code_must_be_lowercase(cls, v):
        return v.lower() if v else v


class ProviderCurrencyResponse(BaseModel):
    """Response from provider API for supported currencies."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool = Field(description="Whether request was successful")
    currencies: List[CurrencyInfo] = Field(default_factory=list, description="List of supported currencies")
    total_count: Optional[int] = Field(None, ge=0, description="Total number of currencies")
    
    # Error information
    error_code: Optional[str] = Field(None, description="Provider error code")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Request metadata
    provider_name: Optional[str] = Field(None, description="Provider name")
    request_timestamp: Optional[str] = Field(None, description="Request timestamp")
    cache_ttl: Optional[int] = Field(None, ge=0, description="Cache TTL in seconds")
    
    @field_validator('currencies')
    @classmethod
    def validate_currency_codes_unique(cls, v):
        codes = [currency.code for currency in v]
        if len(codes) != len(set(codes)):
            raise ValueError('Currency codes must be unique')
        return v


class ProviderNetworkResponse(BaseModel):
    """Response from provider API for supported networks."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool = Field(description="Whether request was successful")
    networks: Dict[str, List[NetworkInfo]] = Field(
        default_factory=dict, 
        description="Networks grouped by currency code"
    )
    
    # Error information
    error_code: Optional[str] = Field(None, description="Provider error code")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Request metadata
    provider_name: Optional[str] = Field(None, description="Provider name")
    request_timestamp: Optional[str] = Field(None, description="Request timestamp")
    cache_ttl: Optional[int] = Field(None, ge=0, description="Cache TTL in seconds")
    
    @field_validator('networks')
    @classmethod
    def validate_network_structure(cls, v):
        for currency_code, networks in v.items():
            if not currency_code.isupper():
                raise ValueError(f'Currency code {currency_code} must be uppercase')
            
            network_codes = [network.code for network in networks]
            if len(network_codes) != len(set(network_codes)):
                raise ValueError(f'Network codes must be unique for currency {currency_code}')
        return v


class CurrencyNetworkMapping(BaseModel):
    """Mapping of currencies to their supported networks."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    provider_name: str = Field(description="Provider name")
    mapping: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Currency code -> List of network codes"
    )
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    
    # Cache information
    cache_key: Optional[str] = Field(None, description="Cache key for this mapping")
    ttl_seconds: Optional[int] = Field(None, ge=0, description="TTL for caching")
    
    @field_validator('mapping')
    @classmethod
    def validate_mapping_structure(cls, v):
        for currency_code, network_codes in v.items():
            if not currency_code.isupper():
                raise ValueError(f'Currency code {currency_code} must be uppercase')
            
            if len(network_codes) != len(set(network_codes)):
                raise ValueError(f'Network codes must be unique for currency {currency_code}')
        return v
    
    def get_networks_for_currency(self, currency_code: str) -> List[str]:
        """Get supported networks for a specific currency."""
        return self.mapping.get(currency_code.upper(), [])
    
    def get_all_currencies(self) -> List[str]:
        """Get all supported currency codes."""
        return list(self.mapping.keys())
    
    def get_all_networks(self) -> List[str]:
        """Get all unique network codes."""
        all_networks = []
        for networks in self.mapping.values():
            all_networks.extend(networks)
        return list(set(all_networks))