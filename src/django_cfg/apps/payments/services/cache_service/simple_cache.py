"""
Simple cache implementation for the Universal Payment System v2.0.

Basic cache functionality with graceful fallback.
"""

from typing import Optional, Any
from django.core.cache import cache
from django_cfg.modules.django_logger import get_logger

from .interfaces import CacheInterface

logger = get_logger(__name__)


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
        from django.conf import settings
        import sys
        
        # For tests, always enable cache (detect test environment)
        if 'test' in sys.argv or hasattr(settings, 'TESTING'):
            return True
            
        # For development, enable by default
        if settings.DEBUG:
            return True
            
        try:
            from django_cfg.models.payments import PaymentsConfig
            config = PaymentsConfig.get_current_config()
            return config.enabled  # Cache enabled if payments enabled
        except Exception as e:
            logger.debug(f"PaymentsConfig not available, enabling cache by default: {e}")
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
