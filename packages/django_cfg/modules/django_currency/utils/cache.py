"""
Simple cache manager for currency rates.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cachetools import TTLCache

from ..core.models import Rate
from ..core.exceptions import CacheError

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple TTL cache for currency rates."""
    
    def __init__(self, ttl: int = 300, maxsize: int = 1000):
        """
        Initialize cache manager.
        
        Args:
            ttl: Time to live in seconds (default 5 minutes)
            maxsize: Maximum cache size (default 1000 items)
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.ttl = ttl
        
    def get_rate(self, base: str, quote: str, source: str) -> Optional[Rate]:
        """
        Get cached rate.
        
        Args:
            base: Base currency
            quote: Quote currency  
            source: Data source
            
        Returns:
            Cached Rate or None
        """
        key = self._make_key(base, quote, source)
        
        try:
            cached_rate = self.cache.get(key)
            if cached_rate:
                logger.debug(f"Cache hit for {key}")
                return cached_rate
            else:
                logger.debug(f"Cache miss for {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set_rate(self, rate: Rate) -> bool:
        """
        Cache rate.
        
        Args:
            rate: Rate to cache
            
        Returns:
            True if cached successfully
        """
        key = self._make_key(rate.base_currency, rate.quote_currency, rate.source)
        
        try:
            self.cache[key] = rate
            logger.debug(f"Cached rate for {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def _make_key(self, base: str, quote: str, source: str) -> str:
        """Make cache key."""
        return f"{source}:{base}:{quote}".upper()
    
    def clear(self) -> None:
        """Clear all cached rates."""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "ttl": self.ttl,
            "currsize": self.cache.currsize
        }
