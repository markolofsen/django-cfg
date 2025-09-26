"""
Cache services for the Universal Payment System v2.0.

Based on proven solutions from payments_old with improvements.
ONLY for API access control - NOT payment data!
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from django.core.cache import cache
from django_cfg.modules.django_logger import get_logger

logger = get_logger(__name__)


class CacheInterface(ABC):
    """Abstract cache interface."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass


class SimpleCache(CacheInterface):
    """
    Simple cache implementation using Django's cache framework.
    
    Falls back gracefully when cache is unavailable.
    Based on proven solution from payments_old.
    """
    
    def __init__(self, prefix: str = "payments"):
        self.prefix = prefix
        self.enabled = self._is_cache_enabled()
    
    def _is_cache_enabled(self) -> bool:
        """Check if cache is enabled via PaymentsConfig."""
        try:
            from django_cfg.models.payments import PaymentsConfig
            config = PaymentsConfig.get_current_config()
            return config.enabled  # Cache enabled if payments enabled
        except Exception:
            return True  # Default to enabled with graceful fallback
        
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.prefix}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
            
        try:
            cache_key = self._make_key(key)
            return cache.get(cache_key)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.enabled:
            return False
            
        try:
            cache_key = self._make_key(key)
            cache.set(cache_key, value, timeout)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.enabled:
            return False
            
        try:
            cache_key = self._make_key(key)
            cache.delete(cache_key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.enabled:
            return False
            
        try:
            cache_key = self._make_key(key)
            return cache.get(cache_key) is not None
        except Exception as e:
            logger.warning(f"Cache exists check failed for key {key}: {e}")
            return False


class ApiKeyCache:
    """Specialized cache for API key operations."""
    
    def __init__(self):
        self.cache = SimpleCache("api_keys")
        self.default_timeout = self._get_cache_timeout('api_key')
    
    def _get_cache_timeout(self, cache_type: str) -> int:
        """Get cache timeout from PaymentsConfig."""
        try:
            from django_cfg.models.payments import PaymentsConfig
            config = PaymentsConfig.get_current_config()
            return config.cache_timeouts.get(cache_type, 300)
        except Exception:
            return 300  # 5 minutes default
    
    def get_api_key_data(self, api_key: str) -> Optional[dict]:
        """Get cached API key data."""
        return self.cache.get(f"key:{api_key}")
    
    def cache_api_key_data(self, api_key: str, data: dict) -> bool:
        """Cache API key data."""
        return self.cache.set(f"key:{api_key}", data, self.default_timeout)
    
    def invalidate_api_key(self, api_key: str) -> bool:
        """Invalidate cached API key."""
        return self.cache.delete(f"key:{api_key}")


class RateLimitCache:
    """Specialized cache for rate limiting."""
    
    def __init__(self):
        self.cache = SimpleCache("rate_limit")
    
    def get_usage_count(self, user_id: int, endpoint_group: str, window: str = "hour") -> int:
        """Get current usage count for rate limiting."""
        key = f"usage:{user_id}:{endpoint_group}:{window}"
        count = self.cache.get(key)
        return count if count is not None else 0
    
    def increment_usage(self, user_id: int, endpoint_group: str, window: str = "hour", ttl: Optional[int] = None) -> int:
        """Increment usage count and return new count."""
        key = f"usage:{user_id}:{endpoint_group}:{window}"
        
        # Get current count
        current = self.get_usage_count(user_id, endpoint_group, window)
        new_count = current + 1
        
        # Get TTL from config or use defaults
        if ttl is None:
            try:
                from django_cfg.models.payments import PaymentsConfig
                config = PaymentsConfig.get_current_config()
                ttl = config.cache_timeouts.get('rate_limit', 3600)
            except Exception:
                ttl = 3600 if window == "hour" else 86400  # 1 hour or 1 day
        
        # Set new count with TTL
        self.cache.set(key, new_count, ttl)
        return new_count
    
    def reset_usage(self, user_id: int, endpoint_group: str, window: str = "hour") -> bool:
        """Reset usage count."""
        key = f"usage:{user_id}:{endpoint_group}:{window}"
        return self.cache.delete(key)


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
