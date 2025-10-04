"""
API Key cache implementation for the Universal Payment System v2.0.

Specialized caching for API key operations and validation.
"""

from typing import Optional
from .simple_cache import SimpleCache


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
