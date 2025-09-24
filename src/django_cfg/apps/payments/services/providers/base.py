"""
Base payment provider interface.

Abstract base class for all payment providers.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from decimal import Decimal

from ..internal_types import ProviderResponse, WebhookData


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""
    
    def __init__(self, config: dict):
        """Initialize provider with config."""
        self.config = config
        self.name = self.__class__.__name__.lower().replace('provider', '')
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    def create_payment(self, payment_data: dict) -> ProviderResponse:
        """
        Create a payment request.
        
        Args:
            amount: Payment amount
            currency: Payment currency
            **kwargs: Additional parameters (order_id, description, etc.)
            
        Returns:
            Dict with payment creation result
        """
        pass
    
    @abstractmethod
    def check_payment_status(self, payment_id: str) -> ProviderResponse:
        """
        Check payment status.
        
        Args:
            payment_id: Payment ID from provider
            
        Returns:
            Dict with payment status
        """
        pass
    
    @abstractmethod
    def process_webhook(self, payload: dict) -> WebhookData:
        """
        Process webhook payload.
        
        Args:
            payload: Webhook data from provider
            
        Returns:
            Dict with processed webhook data
        """
        pass
    
    @abstractmethod
    def get_supported_currencies(self) -> List[str]:
        """
        Get list of supported currencies.
        
        Returns:
            List of supported currency codes
        """
        pass
    
    def validate_webhook(self, payload: dict, headers: Optional[dict] = None) -> bool:
        """
        Validate webhook signature and data.
        
        Args:
            payload: Webhook data
            signature: Webhook signature (if applicable)
            
        Returns:
            True if webhook is valid
        """
        # Default implementation - providers can override
        return True
    
    def get_minimum_payment_amount(self, currency_from: str, currency_to: str = 'usd') -> Optional[Decimal]:
        """
        Get minimum payment amount for currency pair.
        
        Args:
            currency_from: Source currency
            currency_to: Target currency
            
        Returns:
            Minimum payment amount or None if not supported
        """
        # Optional method - providers can override
        return None
    
    def estimate_payment_amount(self, amount: Decimal, currency_code: str) -> Optional[dict]:
        """
        Estimate payment amount in target currency.
        
        Args:
            amount: Amount to estimate
            currency_code: Target currency
            
        Returns:
            Dict with estimation data or None if not supported
        """
        # Optional method - providers can override
        return None
    
    def check_api_status(self) -> bool:
        """
        Check if provider API is available.
        
        Returns:
            True if API is available
        """
        # Optional method - providers can override
        return True
    
    def is_enabled(self) -> bool:
        """Check if provider is enabled."""
        return self.enabled
    
    def get_provider_info(self) -> dict:
        """Get provider information."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'supported_currencies': self.get_supported_currencies(),
            'api_status': self.check_api_status(),
        }
