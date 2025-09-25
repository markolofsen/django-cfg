"""
Configuration utilities for payments module.

Universal utilities for working with django-cfg settings and configuration.
"""

from typing import Optional, Dict, Any, Type
from django.conf import settings

from django_cfg.modules.base import BaseCfgModule
from ..config.settings import PaymentsSettings
from django_cfg.modules.django_logger import get_logger

logger = get_logger("config_utils")


class PaymentsConfigMixin:
    """Mixin for accessing payments configuration through django-cfg."""
    
    _payments_config_cache: Optional[PaymentsSettings] = None
    _config_module: Optional[BaseCfgModule] = None
    
    @classmethod
    def get_payments_config(cls) -> PaymentsSettings:
        """Get payments configuration from django-cfg."""
        if cls._payments_config_cache is None:
            cls._payments_config_cache = cls._load_payments_config()
        return cls._payments_config_cache
    
    @classmethod
    def _load_payments_config(cls) -> PaymentsSettings:
        """Load payments configuration using BaseCfgModule."""
        try:
            if cls._config_module is None:
                from ..config.module import PaymentsCfgModule
                cls._config_module = PaymentsCfgModule()
            
            return cls._config_module.get_config()
        except Exception as e:
            logger.warning(f"Failed to load payments config: {e}")
            return PaymentsSettings()
    
    @classmethod
    def reset_config_cache(cls):
        """Reset configuration cache."""
        cls._payments_config_cache = None
        if cls._config_module:
            cls._config_module.reset_cache()


class RedisConfigHelper(PaymentsConfigMixin):
    """Helper for Redis configuration."""
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration for payments."""
        config = cls.get_payments_config()
        
        # Default Redis settings
        redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'decode_responses': True,
            'socket_timeout': 5,
            'socket_connect_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30,
        }
        
        # Try to get Redis settings from Django CACHES
        django_cache = getattr(settings, 'CACHES', {}).get('default', {})
        if 'redis' in django_cache.get('BACKEND', '').lower():
            location = django_cache.get('LOCATION', '')
            if location.startswith('redis://'):
                # Parse redis://host:port/db format
                try:
                    # Simple parsing for redis://host:port/db
                    parts = location.replace('redis://', '').split('/')
                    host_port = parts[0].split(':')
                    redis_config['host'] = host_port[0]
                    if len(host_port) > 1:
                        redis_config['port'] = int(host_port[1])
                    if len(parts) > 1:
                        redis_config['db'] = int(parts[1])
                except (ValueError, IndexError) as e:
                    logger.warning(f"Failed to parse Redis URL {location}: {e}")
        
        # Override with payments-specific Redis config if available
        if hasattr(config, 'redis') and config.redis:
            redis_config.update(config.redis.dict())
        
        return redis_config
    
    @classmethod
    def is_redis_available(cls) -> bool:
        """Check if Redis is available and configured."""
        try:
            import redis
            config = cls.get_redis_config()
            client = redis.Redis(**config)
            client.ping()
            return True
        except Exception as e:
            logger.debug(f"Redis not available: {e}")
            return False


class CacheConfigHelper(PaymentsConfigMixin):
    """Helper for cache configuration."""
    
    @classmethod
    def get_cache_backend_type(cls) -> str:
        """Get Django cache backend type."""
        django_cache = getattr(settings, 'CACHES', {}).get('default', {})
        backend = django_cache.get('BACKEND', '').lower()
        
        if 'redis' in backend:
            return 'redis'
        elif 'memcached' in backend:
            return 'memcached'
        elif 'database' in backend:
            return 'database'
        elif 'dummy' in backend:
            return 'dummy'
        else:
            return 'unknown'
    
    @classmethod
    def is_cache_enabled(cls) -> bool:
        """Check if cache is properly configured (not dummy)."""
        return cls.get_cache_backend_type() != 'dummy'
    
    @classmethod
    def get_cache_timeout(cls, operation: str) -> int:
        """Get cache timeout for specific operation."""
        config = cls.get_payments_config()
        
        timeouts = {
            'api_key': 300,      # 5 minutes
            'rate_limit': 3600,  # 1 hour
            'session': 1800,     # 30 minutes
            'default': 600       # 10 minutes
        }
        
        # Override with config if available
        if hasattr(config, 'cache_timeouts') and config.cache_timeouts:
            timeouts.update(config.cache_timeouts)
        
        return timeouts.get(operation, timeouts['default'])


class ProviderConfigHelper(PaymentsConfigMixin):
    """Helper for payment provider configuration."""
    
    @classmethod
    def get_enabled_providers(cls) -> list:
        """Get list of enabled payment providers."""
        config = cls.get_payments_config()
        if not config.enabled:
            return []
        
        enabled = []
        if hasattr(config, 'providers') and config.providers:
            for provider_name, provider_config in config.providers.items():
                if provider_config and cls._is_provider_properly_configured(provider_name, provider_config):
                    enabled.append(provider_name)
        
        return enabled
    
    @classmethod
    def get_provider_config(cls, provider_name: str) -> Optional[Any]:
        """Get configuration for specific provider."""
        config = cls.get_payments_config()
        if not config.enabled or not hasattr(config, 'providers'):
            return None
        
        return config.providers.get(provider_name)
    
    @classmethod
    def is_provider_enabled(cls, provider_name: str) -> bool:
        """Check if specific provider is enabled and configured."""
        return provider_name in cls.get_enabled_providers()
    
    @classmethod
    def _is_provider_properly_configured(cls, provider_name: str, provider_config: Any) -> bool:
        """Check if provider configuration is complete."""
        if not provider_config:
            return False
        
        # Basic validation - each provider should have api_key
        if not hasattr(provider_config, 'api_key') or not provider_config.api_key:
            return False
        
        # Provider-specific validations
        if provider_name == 'nowpayments':
            return True  # api_key is sufficient
        elif provider_name == 'stripe':
            return True  # api_key is sufficient
        elif provider_name == 'cryptapi':
            return hasattr(provider_config, 'own_address') and provider_config.own_address
        elif provider_name == 'cryptomus':
            return hasattr(provider_config, 'merchant_uuid') and provider_config.merchant_uuid
        
        return True


class PaymentsConfigUtil:
    """
    Universal utility for payments configuration.
    
    Combines all config helpers into one convenient interface.
    """
    
    redis = RedisConfigHelper
    cache = CacheConfigHelper
    providers = ProviderConfigHelper
    
    @staticmethod
    def get_config() -> PaymentsSettings:
        """Get payments configuration."""
        return PaymentsConfigMixin.get_payments_config()
    
    @staticmethod
    def is_payments_enabled() -> bool:
        """Check if payments module is enabled."""
        config = PaymentsConfigMixin.get_payments_config()
        return config.enabled
    
    
    @staticmethod
    def reset_all_caches():
        """Reset all configuration caches."""
        PaymentsConfigMixin.reset_config_cache()


# Convenience exports
get_payments_config = PaymentsConfigUtil.get_config
is_payments_enabled = PaymentsConfigUtil.is_payments_enabled
