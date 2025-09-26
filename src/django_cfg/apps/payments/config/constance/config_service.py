"""
Configuration service for payments using Constance.

Provides easy access to Constance settings with type safety and caching.
"""

from typing import Dict, Any, Optional
from django_cfg.modules.django_logger import get_logger
from .settings import PaymentConstanceSettings, get_payment_settings

logger = get_logger(__name__)


class PaymentConfigService:
    """
    Service for accessing payment configuration from Constance.
    
    Provides type-safe access to dynamic settings with caching and validation.
    """
    
    def __init__(self):
        """Initialize config service."""
        self._cached_settings: Optional[PaymentConstanceSettings] = None
        self._cache_timeout = 60  # Cache for 1 minute
        self._last_refresh = 0
    
    def get_settings(self, force_refresh: bool = False) -> PaymentConstanceSettings:
        """
        Get current payment settings from Constance.
        
        Args:
            force_refresh: Force refresh from Constance (ignore cache)
            
        Returns:
            PaymentConstanceSettings instance
        """
        import time
        
        current_time = time.time()
        
        if (force_refresh or 
            self._cached_settings is None or 
            (current_time - self._last_refresh) > self._cache_timeout):
            
            try:
                self._cached_settings = get_payment_settings()
                self._last_refresh = current_time
                logger.debug("Refreshed payment settings from Constance")
            except Exception as e:
                logger.error(f"Failed to refresh payment settings: {e}")
                if self._cached_settings is None:
                    # Fallback to defaults if no cache
                    self._cached_settings = PaymentConstanceSettings()
        
        return self._cached_settings
    
    def is_enabled(self) -> bool:
        """Check if payments system is enabled."""
        return self.get_settings().enabled
    
    def is_middleware_enabled(self) -> bool:
        """Check if payments middleware is enabled."""
        return self.get_settings().middleware_enabled
    
    def is_rate_limiting_enabled(self) -> bool:
        """Check if rate limiting is enabled."""
        return self.get_settings().rate_limiting_enabled
    
    def is_usage_tracking_enabled(self) -> bool:
        """Check if usage tracking is enabled."""
        return self.get_settings().usage_tracking_enabled
    
    def get_rate_limits(self) -> Dict[str, int]:
        """Get rate limits configuration."""
        return self.get_settings().get_rate_limits()
    
    def get_cache_timeouts(self) -> Dict[str, int]:
        """Get cache timeouts configuration."""
        return self.get_settings().get_cache_timeouts()
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        return self.get_settings().get_provider_config(provider)
    
    def get_nowpayments_config(self) -> Dict[str, Any]:
        """Get NowPayments configuration."""
        return self.get_provider_config('nowpayments')
    
    def refresh_configuration(self):
        """Force refresh configuration from Constance."""
        self.get_settings(force_refresh=True)
    
    def get_all_provider_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all provider configurations."""
        return {
            'nowpayments': self.get_nowpayments_config(),
        }
    
    def get_constance_settings(self) -> PaymentConstanceSettings:
        """
        Alias for get_settings() for backward compatibility.
        
        Returns:
            PaymentConstanceSettings instance
        """
        return self.get_settings()


# Global instance
_config_service: Optional[PaymentConfigService] = None


def get_payment_config_service() -> PaymentConfigService:
    """
    Get global payment config service instance.
    
    Returns:
        PaymentConfigService instance
    """
    global _config_service
    if _config_service is None:
        _config_service = PaymentConfigService()
    return _config_service
