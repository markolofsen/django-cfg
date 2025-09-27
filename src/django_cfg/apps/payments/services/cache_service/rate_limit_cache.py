"""
Rate limiting cache implementation for the Universal Payment System v2.0.

Specialized caching for API rate limiting and usage tracking.
"""

from typing import Optional
from .simple_cache import SimpleCache


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
