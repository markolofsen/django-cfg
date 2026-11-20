"""Backend selection: one backend per process, chosen from `RealtimeConfig.backend` and `DjangoConfig.redis_url`."""

from __future__ import annotations

import threading
from functools import lru_cache
from typing import TYPE_CHECKING, List, Optional

from .base import Backend, BusItem, Entry, format_offset, parse_offset
from .memory import MemoryBackend

if TYPE_CHECKING:
    from django_cfg.models.django.realtime import RealtimeConfig

_lock = threading.Lock()
_backend: Optional[Backend] = None
# Pushed by `testing.realtime_outbox`; a stack, not a contextvar, so worker threads see it too.
_overrides: List[Backend] = []


def get_realtime_config() -> "RealtimeConfig":
    from django_cfg.core.state.registry import get_current_config

    config = get_current_config()
    realtime = getattr(config, "realtime", None) if config is not None else None
    return realtime if realtime is not None else _default_config()


@lru_cache(maxsize=1)
def _default_config() -> "RealtimeConfig":
    from django_cfg.models.django.realtime import RealtimeConfig

    return RealtimeConfig()


def _redis_url() -> Optional[str]:
    from django_cfg.core.state.registry import get_current_config

    config = get_current_config()
    return getattr(config, "redis_url", None) if config is not None else None


def build_backend() -> Backend:
    """A new backend from config. `backend="redis"` without `redis_url` is a configuration error, not a fallback."""
    config = get_realtime_config()
    ttls = {"history_ttl": config.history_ttl, "meta_ttl": config.meta_ttl}
    url = _redis_url()
    if config.backend == "memory" or (config.backend == "auto" and not url):
        return MemoryBackend(**ttls)
    if not url:
        from django_cfg.core.exceptions import ConfigurationError

        raise ConfigurationError("realtime.backend='redis' needs DjangoConfig.redis_url")
    from .redis_streams import RedisStreamsBackend

    return RedisStreamsBackend(url, pool_size=config.redis_pool_size, pool_timeout=config.redis_pool_timeout, **ttls)


def get_backend() -> Backend:
    if _overrides:
        return _overrides[-1]
    global _backend
    if _backend is None:
        with _lock:
            if _backend is None:
                _backend = build_backend()
    return _backend


def push_backend(backend: Backend) -> None:
    _overrides.append(backend)


def pop_backend(backend: Backend) -> None:
    if backend in _overrides:
        _overrides.remove(backend)


def reset_backend() -> None:
    """Forget the process backend (config changed, tests)."""
    global _backend
    with _lock:
        if _backend is not None:
            _backend.close()
        _backend = None


__all__ = [
    "Backend", "BusItem", "Entry", "MemoryBackend", "format_offset", "parse_offset", "build_backend", "get_backend", "get_realtime_config", "pop_backend",
    "push_backend", "reset_backend",
]
