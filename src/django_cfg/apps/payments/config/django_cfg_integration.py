"""
Django-CFG integration for payments configuration.

Central place for accessing django-cfg PaymentsConfig with proper error handling
and caching. All payments modules should use this for configuration access.
"""

from typing import Optional
from django_cfg.core.config import get_current_config
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payments_django_cfg_integration")


class PaymentsConfigManager:
    """
    Central manager for payments configuration access.
    
    Provides cached, type-safe access to PaymentsConfig from django-cfg
    with proper error handling and fallbacks.
    """
    
    _payments_config_cache: Optional[any] = None
    _cache_timestamp: float = 0
    _cache_ttl: float = 60.0  # Cache for 60 seconds
    
    @classmethod
    def get_payments_config(cls, force_refresh: bool = False):
        """
        Get payments configuration from django-cfg.
        
        Args:
            force_refresh: Force refresh from django-cfg (ignore cache)
            
        Returns:
            PaymentsConfig instance from current django-cfg config
            
        Raises:
            ValueError: If PaymentsConfig not found in current config
        """
        import time
        
        current_time = time.time()
        
        # Check if cache is valid
        if (not force_refresh and 
            cls._payments_config_cache is not None and 
            (current_time - cls._cache_timestamp) < cls._cache_ttl):
            return cls._payments_config_cache
        
        # Load fresh config
        try:
            current_config = get_current_config()
            if current_config and hasattr(current_config, 'payments') and current_config.payments:
                cls._payments_config_cache = current_config.payments
                cls._cache_timestamp = current_time
                logger.debug("Loaded PaymentsConfig from django-cfg")
                return cls._payments_config_cache
            else:
                error_msg = "PaymentsConfig not found in current django-cfg config"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Failed to load payments config: {e}")
            raise
    
    @classmethod
    def get_payments_config_safe(cls, force_refresh: bool = False):
        """
        Get payments configuration with fallback to defaults.
        
        Args:
            force_refresh: Force refresh from django-cfg (ignore cache)
            
        Returns:
            PaymentsConfig instance (from django-cfg or defaults)
        """
        try:
            return cls.get_payments_config(force_refresh=force_refresh)
        except Exception as e:
            logger.warning(f"Using default PaymentsConfig due to error: {e}")
            from django_cfg.models.payments import PaymentsConfig
            return PaymentsConfig()
    
    @classmethod
    def is_payments_enabled(cls) -> bool:
        """
        Check if payments module is enabled.
        
        Returns:
            True if payments is enabled in django-cfg config
        """
        try:
            config = cls.get_payments_config()
            return config.enabled
        except Exception:
            logger.warning("Failed to check payments enabled status, defaulting to False")
            return False
    
    @classmethod
    def is_payments_configured(cls) -> bool:
        """
        Check if payments is properly configured in django-cfg.
        
        Returns:
            True if PaymentsConfig exists in current config
        """
        try:
            cls.get_payments_config()
            return True
        except Exception:
            return False
    
    @classmethod
    def reset_cache(cls):
        """Reset configuration cache."""
        cls._payments_config_cache = None
        cls._cache_timestamp = 0
        logger.debug("PaymentsConfig cache reset")
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        Get summary of current payments configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        try:
            config = cls.get_payments_config()
            return {
                'configured': True,
                'enabled': config.enabled,
                'middleware_enabled': config.middleware_enabled,
                'rate_limiting_enabled': config.rate_limiting_enabled,
                'usage_tracking_enabled': config.usage_tracking_enabled,
                'cache_timeouts': config.cache_timeouts,
                'api_prefixes': config.api_prefixes,
            }
        except Exception as e:
            return {
                'configured': False,
                'error': str(e),
                'enabled': False,
            }


# Legacy compatibility - keep old interface
class PaymentsConfigMixin:
    """Legacy mixin for backward compatibility."""
    
    @classmethod
    def get_payments_config(cls):
        """Get payments configuration from django-cfg."""
        return PaymentsConfigManager.get_payments_config_safe()
    
    @classmethod
    def reset_config_cache(cls):
        """Reset configuration cache."""
        PaymentsConfigManager.reset_cache()


# Public API functions
def get_payments_config(safe: bool = True, force_refresh: bool = False):
    """
    Get payments configuration from django-cfg.
    
    Args:
        safe: If True, return defaults on error. If False, raise exception.
        force_refresh: Force refresh from django-cfg (ignore cache)
        
    Returns:
        PaymentsConfig instance
        
    Raises:
        ValueError: If safe=False and PaymentsConfig not found
    """
    if safe:
        return PaymentsConfigManager.get_payments_config_safe(force_refresh=force_refresh)
    else:
        return PaymentsConfigManager.get_payments_config(force_refresh=force_refresh)


def is_payments_enabled() -> bool:
    """Check if payments module is enabled."""
    return PaymentsConfigManager.is_payments_enabled()


def is_payments_configured() -> bool:
    """Check if payments is properly configured in django-cfg."""
    return PaymentsConfigManager.is_payments_configured()


def get_config_summary() -> dict:
    """Get summary of current payments configuration."""
    return PaymentsConfigManager.get_config_summary()


def reset_payments_config_cache():
    """Reset payments configuration cache."""
    PaymentsConfigManager.reset_cache()