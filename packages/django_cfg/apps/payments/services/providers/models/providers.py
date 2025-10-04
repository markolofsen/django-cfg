"""
Provider enums and metadata for Universal Payment System v2.0.

Provider definitions with comprehensive metadata.
"""

from enum import Enum
from typing import List, Dict
from .base import ProviderMetadata, ProviderType, ProviderStatus


class ProviderEnum(Enum):
    """Enumeration of supported payment providers."""
    
    NOWPAYMENTS = "nowpayments"

    @classmethod
    def get_all_providers(cls) -> List[str]:
        """Get list of all provider values."""
        return [provider.value for provider in cls]
    
    @classmethod
    def is_valid_provider(cls, provider_name: str) -> bool:
        """Check if provider name is valid."""
        return provider_name in cls.get_all_providers()
    
    @classmethod
    def get_crypto_providers(cls) -> List[str]:
        """Get list of crypto-supporting providers."""
        return [
            provider.value for provider in cls
            if PROVIDER_METADATA[provider.value].supports_crypto
        ]
    
    @classmethod
    def get_fiat_providers(cls) -> List[str]:
        """Get list of fiat-supporting providers."""
        return [
            provider.value for provider in cls
            if PROVIDER_METADATA[provider.value].supports_fiat
        ]
    
    @classmethod
    def get_active_providers(cls) -> List[str]:
        """Get list of active providers."""
        return [
            provider.value for provider in cls
            if PROVIDER_METADATA[provider.value].status == ProviderStatus.ACTIVE
        ]


# Provider metadata registry
PROVIDER_METADATA: Dict[str, ProviderMetadata] = {
    ProviderEnum.NOWPAYMENTS.value: ProviderMetadata(
        name="NowPayments",
        provider_type=ProviderType.CRYPTO,
        status=ProviderStatus.ACTIVE,
        priority=10,  # High priority
        
        # Features
        supports_fiat=False,
        supports_crypto=True,
        supports_webhooks=True,
        supports_refunds=False,
        supports_partial_payments=False,
        
        # Limits and fees
        min_amount_usd=1.0,
        max_amount_usd=50000.0,
        fee_percentage=0.5,  # 0.5% fee
        fixed_fee_usd=0.0,
        
        # Geographic
        supported_countries=[],  # Global support
        restricted_countries=["US"],  # Example restriction
        requires_kyc=False,
        
        # Technical
        api_version="v1",
        documentation_url="https://documenter.getpostman.com/view/7907941/S1a32n38",
        status_page_url="https://status.nowpayments.io/",
        
        # Additional
        tags=["crypto", "bitcoin", "ethereum", "altcoins", "instant"],
        description="Cryptocurrency payment processor supporting 300+ cryptocurrencies with instant settlements"
    )
}
