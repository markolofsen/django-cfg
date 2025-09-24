"""
Universal payments module settings.

Core settings for the payments system - now using unified models from django_cfg.models.payments.
"""

from typing import Dict, List
from pydantic import BaseModel, Field

# Import unified types from models/payments.py
from django_cfg.models.payments import (
    PaymentProviderConfig, 
    SecuritySettings, 
    RateLimitSettings, 
    NotificationSettings,
    SubscriptionSettings
)


class PaymentsSettings(BaseModel):
    """Universal payments module settings - unified with PaymentsConfig."""
    
    # General settings
    enabled: bool = Field(default=True, description="Enable payments module")
    debug_mode: bool = Field(default=False, description="Enable debug mode for payments")
    
    # Component settings - using unified models
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    rate_limits: RateLimitSettings = Field(default_factory=RateLimitSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    subscriptions: SubscriptionSettings = Field(default_factory=SubscriptionSettings)
    
    # Provider configurations - now accepts List instead of Dict
    providers: Dict[str, PaymentProviderConfig] = Field(
        default_factory=dict, 
        description="Payment provider configurations (Dict for backwards compatibility)"
    )
    
    # Feature flags - copied from PaymentsConfig for consistency
    enable_crypto_payments: bool = Field(default=True, description="Enable cryptocurrency payments")
    enable_fiat_payments: bool = Field(default=True, description="Enable fiat currency payments")
    enable_subscription_system: bool = Field(default=True, description="Enable subscription system")
    enable_balance_system: bool = Field(default=True, description="Enable user balance system")
    enable_api_key_system: bool = Field(default=True, description="Enable API key system")
    enable_webhook_processing: bool = Field(default=True, description="Enable webhook processing")
    enable_billing_utils: bool = Field(default=True, description="Enable billing utility functions")
    
    # Backwards compatibility properties
    @property
    def auto_create_api_keys(self) -> bool:
        """Backwards compatibility for auto_create_api_keys."""
        return self.security.auto_create_api_keys
    
    @property
    def require_api_key(self) -> bool:
        """Backwards compatibility for require_api_key."""
        return self.security.require_api_key
    
    @property
    def min_balance_threshold(self) -> float:
        """Backwards compatibility for min_balance_threshold."""
        return float(self.security.min_balance_threshold)
    
    @property
    def requests_per_hour(self) -> int:
        """Backwards compatibility for requests_per_hour."""
        return self.rate_limits.requests_per_hour
    
    @property
    def webhook_timeout(self) -> int:
        """Backwards compatibility for webhook_timeout."""
        return self.notifications.webhook_timeout
    
    # Utility methods
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if a specific provider is enabled."""
        provider = self.providers.get(provider_name)
        return provider and provider.enabled if provider else False
    
    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled provider names."""
        return [name for name, config in self.providers.items() if config.enabled]
    
    def get_provider_config(self, provider_name: str) -> PaymentProviderConfig:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)


__all__ = [
    'PaymentsSettings',
    'SecuritySettings',
    'RateLimitSettings', 
    'NotificationSettings',
    'SubscriptionSettings',
    'PaymentProviderConfig'
]