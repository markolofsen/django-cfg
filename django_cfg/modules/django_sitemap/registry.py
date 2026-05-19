"""Process-wide sitemap-source registry.

Apps call `register()` from their `sitemap_sources.py` (autoloaded by
`SitemapAppConfig.ready()`). Re-registering the same `name` replaces —
this is the contract that lets dev autoreload not blow up.
"""
from __future__ import annotations

import logging

from .sources import SitemapSource

logger = logging.getLogger(__name__)

_SOURCES: dict[str, SitemapSource] = {}


def register(source: SitemapSource) -> None:
    if source.name in _SOURCES:
        logger.info("django_sitemap: replacing source %r", source.name)
    _SOURCES[source.name] = source


def get(name: str) -> SitemapSource | None:
    return _SOURCES.get(name)


def all_sources() -> list[SitemapSource]:
    return [s for s in _SOURCES.values() if s.enabled]


def clear() -> None:
    """Test helper — wipe the registry between cases."""
    _SOURCES.clear()
