"""
Simple cache implementation for API keys and rate limiting.
ONLY for API access control - NOT payment data!
"""

from django_cfg.modules.django_logger import get_logger
from typing import Optional, Any
from django.core.cache import cache

from .base import CacheInterface
from ...utils.config_utils import CacheConfigHelper

logger = get_logger("simple_cache")


class SimpleCache(CacheInterface):
    """
    Simple cache implementation using Django's cache framework.
    
    Falls back gracefully when cache is unavailable.
    """
    
    def __init__(self, prefix: str = "payments"):
        self.prefix = prefix
        # Use config helper to check if cache is enabled
        self.enabled = CacheConfigHelper.is_cache_enabled()
        
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
        # Get timeout from config
        self.default_timeout = CacheConfigHelper.get_cache_timeout('api_key')
    
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
        
        # Use config helper for TTL if not provided
        if ttl is None:
            ttl = CacheConfigHelper.get_cache_timeout('rate_limit')
        
        # Set new count with TTL
        self.cache.set(key, new_count, ttl)
        return new_count
    
    def reset_usage(self, user_id: int, endpoint_group: str, window: str = "hour") -> bool:
        """Reset usage count."""
        key = f"usage:{user_id}:{endpoint_group}:{window}"
        return self.cache.delete(key)
