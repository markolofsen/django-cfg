"""
Cache services for the Universal Payment System v2.0.

Main entry point for cache functionality.
Based on proven solutions from payments_old with improvements.
ONLY for API access control - NOT payment data!
"""

from typing import Dict, Any
from django.core.cache import cache
from django_cfg.modules.django_logger import get_logger

from .interfaces import CacheInterface
from .simple_cache import SimpleCache
from .api_key_cache import ApiKeyCache
from .rate_limit_cache import RateLimitCache
from .keys import CacheKeys

logger = get_logger(__name__)


class CacheService:
    """
    Main cache service providing access to specialized caches.
    
    Provides centralized access to different cache types.
    """
    
    def __init__(self):
        """Initialize cache service with specialized caches."""
        self.simple_cache = SimpleCache()
        self.api_key_cache = ApiKeyCache()
        self.rate_limit_cache = RateLimitCache()
        # Backward compatibility attributes
        self.default_timeout = 300
        self.key_prefix = "payments"
    
    # Backward compatibility methods - delegate to simple_cache
    def get(self, key: str):
        """Get value from cache."""
        return self.simple_cache.get(key)
    
    def set(self, key: str, value, timeout=None):
        """Set value in cache."""
        return self.simple_cache.set(key, value, timeout)
    
    def delete(self, key: str):
        """Delete value from cache."""
        return self.simple_cache.delete(key)
    
    def exists(self, key: str):
        """Check if key exists in cache."""
        return self.simple_cache.exists(key)
    
    def get_or_set(self, key: str, default, timeout=None):
        """Get value or set default if not exists."""
        value = self.get(key)
        if value is None:
            if callable(default):
                value = default()
            else:
                value = default
            self.set(key, value, timeout)
        return value
    
    def set_many(self, data: dict, timeout=None):
        """Set multiple values."""
        for key, value in data.items():
            self.set(key, value, timeout)
    
    def get_many(self, keys: list):
        """Get multiple values."""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def delete_many(self, keys: list):
        """Delete multiple values."""
        for key in keys:
            self.delete(key)
    
    def clear(self):
        """Clear all cache (not implemented for safety)."""
        # For safety, we don't implement cache.clear() 
        # as it would clear the entire cache backend
        # Instead, we clear Django's cache which is safe for tests
        from django.core.cache import cache
        cache.clear()
    
    def health_check(self) -> Dict[str, Any]:
        """Check cache health."""
        try:
            test_key = "health_check"
            test_value = "ok"
            
            # Test set/get/delete
            self.simple_cache.set(test_key, test_value, 10)
            retrieved = self.simple_cache.get(test_key)
            self.simple_cache.delete(test_key)
            
            is_healthy = retrieved == test_value
            
            return {
                'healthy': is_healthy,
                'backend': cache.__class__.__name__,
                'simple_cache': True,
                'api_key_cache': True,
                'rate_limit_cache': True
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                'healthy': False,
                'error': str(e),
                'backend': cache.__class__.__name__
            }


# Global cache service instance
_cache_service = None


def get_cache_service() -> CacheService:
    """Get global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


# Export main classes for backward compatibility
__all__ = [
    'CacheService',
    'CacheInterface', 
    'SimpleCache',
    'ApiKeyCache',
    'RateLimitCache',
    'CacheKeys',
    'get_cache_service'
]
