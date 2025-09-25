"""
Payment system configuration models for Django-CFG.

This module provides type-safe Pydantic models for configuring the universal
payment system, including provider configurations, security settings,
and integration options.
"""

from pydantic import BaseModel, Field, SecretStr, field_validator
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PaymentProvider(str, Enum):
    """Supported payment providers."""
    NOWPAYMENTS = "nowpayments"
    CRYPTAPI = "cryptapi"
    STRIPE = "stripe"
    # Future providers can be added here


class BillingPeriod(str, Enum):
    """Supported billing periods."""
    MONTHLY = "monthly"
    YEARLY = "yearly"


class PaymentProviderConfig(BaseModel):
    """Base configuration for payment providers."""
    
    name: str = Field(
        description="Provider name (e.g., 'nowpayments', 'cryptapi', 'stripe')"
    )
    enabled: bool = Field(
        default=True, 
        description="Enable this payment provider"
    )
    sandbox: bool = Field(
        default=True, 
        description="Use sandbox/test mode"
    )
    api_key: SecretStr = Field(
        description="Provider API key (stored securely)"
    )
    timeout: int = Field(
        default=30, 
        ge=5, 
        le=300, 
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3, 
        ge=0, 
        le=10, 
        description="Maximum retry attempts for failed requests"
    )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary for provider initialization."""
        return {
            'enabled': self.enabled,
            'api_key': self.api_key.get_secret_value(),
            'sandbox': self.sandbox,
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }


class NowPaymentsConfig(PaymentProviderConfig):
    """NowPayments cryptocurrency provider configuration."""
    
    ipn_secret: Optional[SecretStr] = Field(
        default=None, 
        description="IPN secret for webhook validation"
    )
    callback_url: Optional[str] = Field(
        default=None, 
        description="Custom webhook callback URL"
    )
    success_url: Optional[str] = Field(
        default=None, 
        description="Payment success redirect URL"
    )
    cancel_url: Optional[str] = Field(
        default=None, 
        description="Payment cancellation redirect URL"
    )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration with NowPayments-specific fields."""
        config = super().get_config_dict()
        config.update({
            'ipn_secret': self.ipn_secret.get_secret_value() if self.ipn_secret else None,
            'callback_url': self.callback_url,
            'success_url': self.success_url,
            'cancel_url': self.cancel_url
        })
        return config


class CryptAPIConfig(PaymentProviderConfig):
    """CryptAPI cryptocurrency provider configuration."""
    
    own_address: str = Field(
        description="Your cryptocurrency wallet address"
    )
    callback_url: Optional[str] = Field(
        default=None, 
        description="Webhook callback URL"
    )
    convert_payments: bool = Field(
        default=False, 
        description="Convert payments to your currency"
    )
    multi_token: bool = Field(
        default=False, 
        description="Enable multi-token support"
    )
    priority: str = Field(
        default="default", 
        description="Transaction priority level"
    )
    
    # CryptAPI doesn't use traditional API keys
    api_key: SecretStr = Field(
        default=SecretStr("not_required"), 
        description="Not required for CryptAPI"
    )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration with CryptAPI-specific fields."""
        config = super().get_config_dict()
        config.update({
            'own_address': self.own_address,
            'callback_url': self.callback_url,
            'convert_payments': self.convert_payments,
            'multi_token': self.multi_token,
            'priority': self.priority
        })
        return config


class StripeConfig(PaymentProviderConfig):
    """Stripe payment provider configuration."""
    
    publishable_key: Optional[str] = Field(
        default=None, 
        description="Stripe publishable key for frontend"
    )
    webhook_endpoint_secret: Optional[SecretStr] = Field(
        default=None, 
        description="Webhook endpoint secret for signature validation"
    )
    success_url: Optional[str] = Field(
        default=None, 
        description="Payment success redirect URL"
    )
    cancel_url: Optional[str] = Field(
        default=None, 
        description="Payment cancellation redirect URL"
    )
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration with Stripe-specific fields."""
        config = super().get_config_dict()
        config.update({
            'publishable_key': self.publishable_key,
            'webhook_endpoint_secret': self.webhook_endpoint_secret.get_secret_value() if self.webhook_endpoint_secret else None,
            'success_url': self.success_url,
            'cancel_url': self.cancel_url
        })
        return config


class SecuritySettings(BaseModel):
    """Security configuration for payments."""
    
    auto_create_api_keys: bool = Field(
        default=True, 
        description="Automatically create API keys for new users"
    )
    require_api_key: bool = Field(
        default=True, 
        description="Require API key for payment endpoints"
    )
    min_balance_threshold: Decimal = Field(
        default=Decimal('0.01'), 
        ge=0, 
        description="Minimum balance threshold for operations"
    )
    max_payment_amount: Decimal = Field(
        default=Decimal('50000.00'), 
        gt=0, 
        description="Maximum payment amount in USD"
    )
    webhook_signature_validation: bool = Field(
        default=True, 
        description="Validate webhook signatures"
    )


class RateLimitSettings(BaseModel):
    """Rate limiting configuration."""
    
    enabled: bool = Field(
        default=True, 
        description="Enable rate limiting"
    )
    requests_per_hour: int = Field(
        default=1000, 
        ge=1, 
        description="Maximum requests per hour per user"
    )
    payment_requests_per_hour: int = Field(
        default=100, 
        ge=1, 
        description="Maximum payment requests per hour per user"
    )
    webhook_requests_per_minute: int = Field(
        default=60, 
        ge=1, 
        description="Maximum webhook requests per minute"
    )


class NotificationSettings(BaseModel):
    """Notification configuration."""
    
    email_notifications: bool = Field(
        default=True, 
        description="Send email notifications for payment events"
    )
    webhook_notifications: bool = Field(
        default=True, 
        description="Send webhook notifications"
    )
    webhook_timeout: int = Field(
        default=30, 
        ge=5, 
        le=300, 
        description="Webhook timeout in seconds"
    )


class SubscriptionSettings(BaseModel):
    """Subscription system configuration."""
    
    enabled: bool = Field(
        default=True, 
        description="Enable subscription system"
    )
    auto_renewal: bool = Field(
        default=True, 
        description="Enable automatic subscription renewal"
    )
    grace_period_days: int = Field(
        default=3, 
        ge=0, 
        le=30, 
        description="Grace period for expired subscriptions"
    )
    trial_period_days: int = Field(
        default=7, 
        ge=0, 
        le=90, 
        description="Default trial period in days"
    )
    refund_policy: Literal["none", "prorated", "full"] = Field(
        default="prorated", 
        description="Default refund policy"
    )


class PaymentsConfig(BaseModel):
    """
    Universal payment system configuration.
    
    This model provides comprehensive configuration for the django-cfg payments
    module, including provider settings, security options, rate limiting,
    and feature toggles.
    """
    
    # === Core Settings ===
    enabled: bool = Field(
        default=True, 
        description="Enable the payments module"
    )
    debug_mode: bool = Field(
        default=False, 
        description="Enable debug mode for detailed logging"
    )
    strict_mode: bool = Field(
        default=True, 
        description="Enable strict validation and security checks"
    )
    
    
    # === Payment Providers ===
    providers: List[PaymentProviderConfig] = Field(
        default_factory=list, 
        description="Payment provider configurations"
    )
    
    # === Feature Configuration ===
    security: SecuritySettings = Field(
        default_factory=SecuritySettings, 
        description="Security settings"
    )
    rate_limits: RateLimitSettings = Field(
        default_factory=RateLimitSettings, 
        description="Rate limiting settings"
    )
    notifications: NotificationSettings = Field(
        default_factory=NotificationSettings, 
        description="Notification settings"
    )
    subscriptions: SubscriptionSettings = Field(
        default_factory=SubscriptionSettings, 
        description="Subscription system settings"
    )
    
    # === Feature Flags ===
    enable_crypto_payments: bool = Field(
        default=True, 
        description="Enable cryptocurrency payments"
    )
    enable_fiat_payments: bool = Field(
        default=True, 
        description="Enable fiat currency payments"
    )
    enable_subscription_system: bool = Field(
        default=True, 
        description="Enable subscription management"
    )
    enable_balance_system: bool = Field(
        default=True, 
        description="Enable user balance system"
    )
    enable_api_key_system: bool = Field(
        default=True, 
        description="Enable API key management"
    )
    enable_webhook_processing: bool = Field(
        default=True, 
        description="Enable webhook processing"
    )
    enable_billing_utils: bool = Field(
        default=True, 
        description="Enable billing utilities and calculations"
    )
    
    # === Middleware Configuration ===
    middleware_enabled: bool = Field(
        default=True, 
        description="Enable payments middleware"
    )
    custom_middleware: List[str] = Field(
        default_factory=list, 
        description="Additional custom middleware classes"
    )
    
    # === URL Configuration ===
    url_prefix: str = Field(
        default="api/payments", 
        description="URL prefix for payment endpoints"
    )
    webhook_url_prefix: str = Field(
        default="webhooks", 
        description="URL prefix for webhook endpoints"
    )
    
    @field_validator("providers")
    @classmethod
    def validate_providers(cls, v: List[PaymentProviderConfig]) -> List[PaymentProviderConfig]:
        """Validate payment provider configurations."""
        if not isinstance(v, list):
            raise ValueError("Providers must be a list")
        
        # Check for duplicate provider names
        names = [provider.name for provider in v]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate provider names found")
        
        # Validate at least one provider is configured if payments are enabled
        enabled_providers = [provider.name for provider in v if provider.enabled]
        if not enabled_providers:
            logger.warning("No payment providers are enabled")
        
        return v
    
    @field_validator("url_prefix", "webhook_url_prefix")
    @classmethod
    def validate_url_prefixes(cls, v: str) -> str:
        """Validate URL prefixes."""
        if not v:
            raise ValueError("URL prefix cannot be empty")
        
        # Remove leading/trailing slashes for consistency
        v = v.strip("/")
        
        # Basic validation
        if not v.replace("/", "").replace("-", "").replace("_", "").isalnum():
            raise ValueError("URL prefix must contain only alphanumeric characters, hyphens, underscores, and slashes")
        
        return v
    
    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled payment providers."""
        return [
            name for name, config in self.providers.items() 
            if config.enabled
        ]
    
    def get_provider_config(self, provider_name: str) -> Optional[PaymentProviderConfig]:
        """Get configuration for specific provider."""
        return self.providers.get(provider_name)
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if specific provider is enabled."""
        config = self.get_provider_config(provider_name)
        return config is not None and config.enabled
    
    def get_middleware_classes(self) -> List[str]:
        """Get list of middleware classes to enable."""
        middleware = []
        
        if not self.middleware_enabled:
            return middleware
        
        if self.enable_api_key_system:
            middleware.append("django_cfg.apps.payments.middleware.APIAccessMiddleware")
        
        if self.rate_limits.enabled:
            middleware.append("django_cfg.apps.payments.middleware.RateLimitingMiddleware")
        
        if self.enable_subscription_system:
            middleware.append("django_cfg.apps.payments.middleware.UsageTrackingMiddleware")
        
        # Add custom middleware
        middleware.extend(self.custom_middleware)
        
        return middleware
    
    def should_enable_tasks(self) -> bool:
        """
        Determine if background tasks should be enabled for payments.
        
        Tasks are enabled if webhook processing is enabled.
        """
        return self.enabled and self.enable_webhook_processing


# Helper function for easy provider configuration
def create_nowpayments_config(
    api_key: str,
    ipn_secret: Optional[str] = None,
    **kwargs
) -> NowPaymentsConfig:
    """Helper to create NowPayments configuration."""
    return NowPaymentsConfig(
        name="nowpayments",
        api_key=SecretStr(api_key),
        ipn_secret=SecretStr(ipn_secret) if ipn_secret else None,
        **kwargs
    )


def create_cryptapi_config(
    own_address: str,
    callback_url: Optional[str] = None,
    **kwargs
) -> CryptAPIConfig:
    """Helper to create CryptAPI configuration."""
    return CryptAPIConfig(
        name="cryptapi",
        own_address=own_address,
        callback_url=callback_url,
        **kwargs
    )


def create_stripe_config(
    api_key: str,
    publishable_key: Optional[str] = None,
    webhook_endpoint_secret: Optional[str] = None,
    **kwargs
) -> StripeConfig:
    """Helper to create Stripe configuration with automatic sandbox detection."""
    return StripeConfig(
        name="stripe",
        api_key=SecretStr(api_key),
        publishable_key=publishable_key,
        webhook_endpoint_secret=SecretStr(webhook_endpoint_secret) if webhook_endpoint_secret else None,
        **kwargs
    )


def create_cryptomus_config(
    api_key: str,
    merchant_uuid: str,
    callback_url: Optional[str] = None,
    success_url: Optional[str] = None,
    fail_url: Optional[str] = None,
    **kwargs
):
    """Helper to create Cryptomus configuration with automatic sandbox detection."""
    # Import here to avoid circular imports
    from django_cfg.apps.payments.config.providers import CryptomusConfig
    
    return CryptomusConfig(
        name="cryptomus",
        api_key=SecretStr(api_key),
        merchant_uuid=merchant_uuid,
        callback_url=callback_url,
        success_url=success_url,
        fail_url=fail_url,
        **kwargs
    )


__all__ = [
    "PaymentsConfig",
    "PaymentProviderConfig", 
    "NowPaymentsConfig",
    "CryptAPIConfig", 
    "StripeConfig",
    "SecuritySettings",
    "RateLimitSettings", 
    "NotificationSettings",
    "SubscriptionSettings",
    "PaymentProvider",
    "BillingPeriod",
    "create_nowpayments_config",
    "create_cryptapi_config", 
    "create_stripe_config",
    "create_cryptomus_config",
]
