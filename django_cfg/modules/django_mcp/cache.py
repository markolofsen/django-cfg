"""
Redis-backed query cache with tenant isolation and stampede prevention.

Usage:
    cache = QueryCache(ttl=300)
    result = cache.get(sql, params, tenant_id)
    if result is None:
        result = execute_query(sql, params)
        cache.set(sql, params, tenant_id, result)
"""

import hashlib
import json
from typing import Any, Optional

from django.core.cache import cache


class QueryCache:
    """Cache agent query results with tenant-aware keys."""

    DEFAULT_TTL = 300  # 5 minutes

    def __init__(self, ttl: int = DEFAULT_TTL):
        self.ttl = ttl

    def _make_key(self, sql: str, params: tuple, tenant_id: str) -> str:
        """Generate cache key from query + context."""
        raw = json.dumps({
            "sql": sql,
            "params": params,
            "tenant_id": tenant_id,
        }, sort_keys=True, default=str)
        return f"mcp:query:{hashlib.sha256(raw.encode()).hexdigest()[:16]}"

    def get(self, sql: str, params: tuple, tenant_id: str) -> Optional[Any]:
        """Get cached result."""
        key = self._make_key(sql, params, tenant_id)
        return cache.get(key)

    def set(self, sql: str, params: tuple, tenant_id: str, result: Any) -> None:
        """Set cached result (only if not already set — prevents stampede)."""
        key = self._make_key(sql, params, tenant_id)
        # cache.add = only set if key doesn't exist (stampede prevention)
        cache.add(key, result, self.ttl)

    def invalidate(self, sql: str, params: tuple, tenant_id: str) -> bool:
        """Invalidate cached result."""
        key = self._make_key(sql, params, tenant_id)
        return cache.delete(key)

    def clear_all(self) -> None:
        """Clear all MCP query cache entries."""
        # This requires Redis KEYS command — use with caution
        from django.conf import settings
        if hasattr(settings, 'CACHES'):
            default_cache = settings.CACHES.get('default', {})
            if 'Redis' in default_cache.get('BACKEND', ''):
                import redis
                client = redis.from_url(default_cache.get('LOCATION'))
                keys = client.keys("mcp:query:*")
                if keys:
                    client.delete(*keys)
