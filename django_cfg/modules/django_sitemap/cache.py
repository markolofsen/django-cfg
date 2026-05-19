"""Redis cache wrappers with versioned keys.

Keys include a cache_version constant from `SitemapConfig` — bump the
constant to invalidate every sitemap cache entry globally without needing
a Redis FLUSH.
"""
from __future__ import annotations

import hashlib
from typing import Any

from django.core.cache import cache

from .config import get_sitemap_config


def _v() -> str:
    return get_sitemap_config().cache_version


def index_key() -> str:
    return f"sitemap:index:{_v()}"


def feed_key(source: str, cursor: str | None) -> str:
    digest = hashlib.sha1((cursor or "").encode("utf-8")).hexdigest()[:16]
    return f"sitemap:feed:{source}:{digest}:{_v()}"


def cache_get(key: str) -> Any:
    return cache.get(key)


def cache_set(key: str, value: Any, ttl_seconds: int) -> None:
    cache.set(key, value, timeout=ttl_seconds)
