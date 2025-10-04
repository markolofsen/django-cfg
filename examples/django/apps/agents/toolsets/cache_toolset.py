"""
Django cache toolset for caching operations.
"""

import logging
from typing import Any, Optional, Dict, List
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai import RunContext
from django.core.cache import cache, caches

from ..core.dependencies import DjangoDeps

logger = logging.getLogger(__name__)


class CacheToolset(AbstractToolset[DjangoDeps]):
    """
    Django cache toolset for caching operations.
    
    Provides tools for:
    - Cache get/set operations
    - Cache key management
    - Cache statistics
    - Multi-cache support
    """
    
    def __init__(self, cache_alias: str = 'default', key_prefix: str = 'orchestrator'):
        """
        Initialize cache toolset.
        
        Args:
            cache_alias: Django cache alias to use
            key_prefix: Prefix for all cache keys
        """
        self.cache_alias = cache_alias
        self.key_prefix = key_prefix
    
    @property
    def id(self) -> str:
        return f"django_cache_{self.cache_alias}"
    
    def _get_cache(self):
        """Get cache instance."""
        if self.cache_alias == 'default':
            return cache
        else:
            return caches[self.cache_alias]
    
    def _make_key(self, key: str, user_id: Optional[int] = None) -> str:
        """Create cache key with prefix and optional user scope."""
        parts = [self.key_prefix]
        
        if user_id:
            parts.append(f"user_{user_id}")
        
        parts.append(key)
        
        return ':'.join(parts)
    
    async def get_cached_value(
        self, 
        ctx: RunContext[DjangoDeps], 
        key: str,
        user_scoped: bool = False
    ) -> Any:
        """Get value from cache."""
        cache_instance = self._get_cache()
        
        user_id = ctx.deps.user.id if user_scoped else None
        cache_key = self._make_key(key, user_id)
        
        try:
            value = cache_instance.get(cache_key)
            logger.debug(f"Cache get: {cache_key} -> {'HIT' if value is not None else 'MISS'}")
            return value
        except Exception as e:
            logger.error(f"Cache get failed for key '{cache_key}': {e}")
            return None
    
    async def set_cached_value(
        self, 
        ctx: RunContext[DjangoDeps], 
        key: str,
        value: Any,
        timeout: Optional[int] = None,
        user_scoped: bool = False
    ) -> bool:
        """Set value in cache."""
        cache_instance = self._get_cache()
        
        user_id = ctx.deps.user.id if user_scoped else None
        cache_key = self._make_key(key, user_id)
        
        try:
            cache_instance.set(cache_key, value, timeout)
            logger.debug(f"Cache set: {cache_key} (timeout: {timeout})")
            return True
        except Exception as e:
            logger.error(f"Cache set failed for key '{cache_key}': {e}")
            return False
    
    async def delete_cached_value(
        self, 
        ctx: RunContext[DjangoDeps], 
        key: str,
        user_scoped: bool = False
    ) -> bool:
        """Delete value from cache."""
        cache_instance = self._get_cache()
        
        user_id = ctx.deps.user.id if user_scoped else None
        cache_key = self._make_key(key, user_id)
        
        try:
            result = cache_instance.delete(cache_key)
            logger.debug(f"Cache delete: {cache_key} -> {result}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete failed for key '{cache_key}': {e}")
            return False
    
    async def get_or_set_cached_value(
        self, 
        ctx: RunContext[DjangoDeps], 
        key: str,
        default_value: Any,
        timeout: Optional[int] = None,
        user_scoped: bool = False
    ) -> Any:
        """Get value from cache or set default if not exists."""
        cache_instance = self._get_cache()
        
        user_id = ctx.deps.user.id if user_scoped else None
        cache_key = self._make_key(key, user_id)
        
        try:
            value = cache_instance.get_or_set(cache_key, default_value, timeout)
            logger.debug(f"Cache get_or_set: {cache_key}")
            return value
        except Exception as e:
            logger.error(f"Cache get_or_set failed for key '{cache_key}': {e}")
            return default_value
    
    async def increment_cached_value(
        self, 
        ctx: RunContext[DjangoDeps], 
        key: str,
        delta: int = 1,
        user_scoped: bool = False
    ) -> Optional[int]:
        """Increment numeric value in cache."""
        cache_instance = self._get_cache()
        
        user_id = ctx.deps.user.id if user_scoped else None
        cache_key = self._make_key(key, user_id)
        
        try:
            # Check if cache backend supports increment
            if hasattr(cache_instance, 'incr'):
                try:
                    value = cache_instance.incr(cache_key, delta)
                    logger.debug(f"Cache increment: {cache_key} += {delta} -> {value}")
                    return value
                except ValueError:
                    # Key doesn't exist, set initial value
                    cache_instance.set(cache_key, delta)
                    return delta
            else:
                # Fallback for backends without increment support
                current = cache_instance.get(cache_key, 0)
                new_value = current + delta
                cache_instance.set(cache_key, new_value)
                return new_value
        except Exception as e:
            logger.error(f"Cache increment failed for key '{cache_key}': {e}")
            return None
    
    async def get_cache_keys(
        self, 
        ctx: RunContext[DjangoDeps], 
        pattern: Optional[str] = None,
        user_scoped: bool = False
    ) -> List[str]:
        """Get cache keys matching pattern."""
        cache_instance = self._get_cache()
        
        # This is backend-dependent and may not work with all cache backends
        try:
            if hasattr(cache_instance, 'keys'):
                if pattern:
                    user_id = ctx.deps.user.id if user_scoped else None
                    search_pattern = self._make_key(pattern, user_id)
                    keys = cache_instance.keys(search_pattern)
                else:
                    keys = cache_instance.keys(f"{self.key_prefix}:*")
                
                return list(keys)
            else:
                logger.warning("Cache backend does not support key listing")
                return []
        except Exception as e:
            logger.error(f"Failed to get cache keys: {e}")
            return []
    
    async def clear_user_cache(self, ctx: RunContext[DjangoDeps]) -> bool:
        """Clear all cache entries for current user."""
        user_id = ctx.deps.user.id
        pattern = f"{self.key_prefix}:user_{user_id}:*"
        
        try:
            keys = await self.get_cache_keys(ctx, pattern="*", user_scoped=True)
            
            if keys:
                cache_instance = self._get_cache()
                cache_instance.delete_many(keys)
                logger.info(f"Cleared {len(keys)} cache entries for user {user_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear user cache for user {user_id}: {e}")
            return False
    
    async def get_cache_stats(self, ctx: RunContext[DjangoDeps]) -> Dict[str, Any]:
        """Get cache statistics (if supported by backend)."""
        cache_instance = self._get_cache()
        
        stats = {
            'cache_alias': self.cache_alias,
            'key_prefix': self.key_prefix,
            'backend': cache_instance.__class__.__name__,
        }
        
        try:
            # Try to get backend-specific stats
            if hasattr(cache_instance, '_cache') and hasattr(cache_instance._cache, 'get_stats'):
                # Memcached backend
                backend_stats = cache_instance._cache.get_stats()
                stats['backend_stats'] = backend_stats
            elif hasattr(cache_instance, 'info'):
                # Redis backend
                info = cache_instance.info()
                stats['backend_stats'] = {
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'total_commands_processed': info.get('total_commands_processed'),
                }
            
            # Get key count if possible
            keys = await self.get_cache_keys(ctx)
            stats['total_keys'] = len(keys)
            
        except Exception as e:
            logger.warning(f"Could not get cache stats: {e}")
            stats['error'] = str(e)
        
        return stats
    
    async def touch_cached_value(
        self, 
        ctx: RunContext[DjangoDeps], 
        key: str,
        timeout: Optional[int] = None,
        user_scoped: bool = False
    ) -> bool:
        """Update cache key timeout without changing value."""
        cache_instance = self._get_cache()
        
        user_id = ctx.deps.user.id if user_scoped else None
        cache_key = self._make_key(key, user_id)
        
        try:
            if hasattr(cache_instance, 'touch'):
                result = cache_instance.touch(cache_key, timeout)
                logger.debug(f"Cache touch: {cache_key} -> {result}")
                return result
            else:
                # Fallback: get and set with new timeout
                value = cache_instance.get(cache_key)
                if value is not None:
                    cache_instance.set(cache_key, value, timeout)
                    return True
                return False
        except Exception as e:
            logger.error(f"Cache touch failed for key '{cache_key}': {e}")
            return False
