"""
Constance settings integration for Payments app.

Simplified settings management using Pydantic models and Constance.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from django_cfg.modules.django_logger import get_logger

logger = get_logger(__name__)


class PaymentConstanceSettings(BaseModel):
    """
    Pydantic model for payments Constance settings.
    
    Provides type-safe access to dynamic settings with validation.
    """
    
    # Core settings
    enabled: bool = Field(default=True, description="Enable payments system")
    middleware_enabled: bool = Field(default=True, description="Enable payments middleware")
    
    # Rate limiting
    rate_limiting_enabled: bool = Field(default=True, description="Enable rate limiting")
    anonymous_rate_limit: int = Field(default=60, description="Anonymous user rate limit")
    authenticated_rate_limit: int = Field(default=300, description="Authenticated user rate limit")
    
    # Usage tracking
    usage_tracking_enabled: bool = Field(default=True, description="Enable usage tracking")
    track_anonymous_usage: bool = Field(default=False, description="Track anonymous usage")
    
    # Cache timeouts
    api_key_cache_timeout: int = Field(default=300, description="API key cache timeout")
    rate_limit_cache_timeout: int = Field(default=3600, description="Rate limit cache timeout")
    session_cache_timeout: int = Field(default=1800, description="Session cache timeout")
    default_cache_timeout: int = Field(default=600, description="Default cache timeout")
    
    # Provider settings
    nowpayments_api_key: str = Field(default="", description="NowPayments API key")
    nowpayments_ipn_secret: str = Field(default="", description="NowPayments IPN secret")
    nowpayments_sandbox_mode: bool = Field(default=True, description="NowPayments sandbox mode")
    
    # Currency settings
    auto_update_rates: bool = Field(default=True, description="Auto update currency rates")
    rate_update_interval_hours: int = Field(default=1, description="Rate update interval")
    
    @classmethod
    def from_constance(cls) -> 'PaymentConstanceSettings':
        """
        Create instance from Constance settings.
        
        Returns:
            PaymentConstanceSettings instance with current Constance values
        """
        try:
            from constance import config
            from ..django_cfg_integration import PaymentsConfigManager
            
            # Get defaults from initialized Pydantic config using PaymentsConfigManager
            pydantic_config = PaymentsConfigManager.get_payments_config()
            
            return cls(
                # Static settings from Pydantic (not in Constance anymore)
                enabled=pydantic_config.enabled,
                middleware_enabled=pydantic_config.middleware_enabled,
                rate_limiting_enabled=pydantic_config.rate_limiting_enabled,
                anonymous_rate_limit=pydantic_config.default_rate_limits['anonymous'],
                authenticated_rate_limit=pydantic_config.default_rate_limits['authenticated'],
                usage_tracking_enabled=pydantic_config.usage_tracking_enabled,
                
                # Dynamic settings from Constance (only what's actually in Constance)
                track_anonymous_usage=getattr(config, 'PAYMENTS_TRACK_ANONYMOUS_USAGE', pydantic_config.track_anonymous_usage),
                
                # Cache timeouts from Pydantic (not in Constance anymore)
                api_key_cache_timeout=pydantic_config.cache_timeouts['api_key'],
                rate_limit_cache_timeout=pydantic_config.cache_timeouts['rate_limit'],
                session_cache_timeout=pydantic_config.cache_timeouts['session'],
                default_cache_timeout=pydantic_config.cache_timeouts['default'],
                
                # Provider settings from Constance (sensitive data)
                nowpayments_api_key=getattr(config, 'PAYMENTS_NOWPAYMENTS_API_KEY', ''),
                nowpayments_ipn_secret=getattr(config, 'PAYMENTS_NOWPAYMENTS_IPN_SECRET', ''),
                nowpayments_sandbox_mode=getattr(config, 'PAYMENTS_NOWPAYMENTS_SANDBOX_MODE', True),
                
                # Currency settings from Pydantic (automatic now)
                auto_update_rates=True,  # Always automatic
                rate_update_interval_hours=1,  # Fixed interval
            )
        except ImportError:
            logger.warning("Constance not available, using default settings")
            return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy access."""
        return self.model_dump()
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get rate limits as dictionary."""
        return {
            'anonymous': self.anonymous_rate_limit,
            'authenticated': self.authenticated_rate_limit,
        }
    
    def get_cache_timeouts(self) -> Dict[str, int]:
        """Get cache timeouts as dictionary."""
        return {
            'api_key': self.api_key_cache_timeout,
            'rate_limit': self.rate_limit_cache_timeout,
            'session': self.session_cache_timeout,
            'default': self.default_cache_timeout,
        }
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        if provider.lower() == 'nowpayments':
            # Provider is enabled if it has API key configured
            is_enabled = bool(self.nowpayments_api_key and self.nowpayments_api_key.strip())
            return {
                'enabled': is_enabled,
                'api_key': self.nowpayments_api_key,
                'ipn_secret': self.nowpayments_ipn_secret,
                'sandbox_mode': self.nowpayments_sandbox_mode,
            }
        return {}


def get_payment_settings() -> PaymentConstanceSettings:
    """
    Get current payment settings from Constance.
    
    Returns:
        PaymentConstanceSettings instance with current values
    """
    return PaymentConstanceSettings.from_constance()


def is_feature_enabled(feature: str) -> bool:
    """
    Check if a specific feature is enabled.
    
    Args:
        feature: Feature name (e.g., 'rate_limiting', 'usage_tracking')
        
    Returns:
        True if feature is enabled, False otherwise
    """
    settings = get_payment_settings()
    
    feature_map = {
        'payments': settings.enabled,
        'middleware': settings.middleware_enabled,
        'rate_limiting': settings.rate_limiting_enabled,
        'usage_tracking': settings.usage_tracking_enabled,
        'anonymous_tracking': settings.track_anonymous_usage,
        'auto_rates': settings.auto_update_rates,
    }
    
    return feature_map.get(feature, False)
