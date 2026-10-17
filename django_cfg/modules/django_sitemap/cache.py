"""Redis cache wrappers with versioned keys.

Keys include a cache_version constant from `SitemapConfig` — bump the
constant to invalidate every sitemap cache entry globally without needing
a Redis FLUSH.
"""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Callable

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


# ── single flight ───────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

#: The holder of a build lock owns it for at most this long; it expires by
#: itself if the process dies. Above the slowest build seen (~90 s on 2.2M rows).
BUILD_LOCK_SECONDS = 600
#: How long a request that lost the race waits for the winner's result before it
#: gives up with None. Waiting costs a worker thread, not a database connection.
BUILD_WAIT_SECONDS = 45.0
_POLL_SECONDS = 0.5


def get_or_build(
    key: str,
    build: Callable[[], Any],
    ttl_seconds: int,
    *,
    lock_seconds: int = BUILD_LOCK_SECONDS,
    wait_seconds: float = BUILD_WAIT_SECONDS,
) -> Any:
    """The cached value, building it at most once at a time on a miss.

    Without this, every request that arrives while the key is missing builds the
    value itself. The index build streams every sitemap row (~90 s on a catalogue
    of 2.2M) and each of those requests holds a database connection for it, so a
    cold key under crawler traffic is a connection-pool outage: on 2026-10-17 the
    consuming project saw 1 784 pool timeouts in two minutes, twice in an hour.

    One caller wins the lock and builds. The others wait for the cache to fill and
    return that value; if it does not appear within `wait_seconds` they return
    None and the view answers 503 + Retry-After rather than start a second build.
    A lock whose holder died expires after `lock_seconds`, and a waiter then
    takes it over.
    """
    cached = cache_get(key)
    if cached is not None:
        return cached

    lock_key = f"{key}:build-lock"
    deadline = time.monotonic() + wait_seconds
    while True:
        if cache.add(lock_key, "1", lock_seconds):
            try:
                # Someone may have finished between our miss and our lock.
                cached = cache_get(key)
                if cached is not None:
                    return cached
                value = build()
                cache_set(key, value, ttl_seconds)
                return value
            finally:
                cache.delete(lock_key)

        if time.monotonic() >= deadline:
            logger.warning("sitemap build for %s still running after %.0fs; not waiting", key, wait_seconds)
            return None
        time.sleep(_POLL_SECONDS)
        cached = cache_get(key)
        if cached is not None:
            return cached
