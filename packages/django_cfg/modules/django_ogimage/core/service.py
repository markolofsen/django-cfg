"""
get_or_create_og_url — main entry point for OG image generation.

Renders on first call, returns cached file URL on subsequent calls.
Cache layout (sharded like Git objects):
    MEDIA_ROOT/ogimage/<key[:2]>/<key[2:4]>/<key>.png
"""
from __future__ import annotations

import logging

from .params import OGImageParams, compute_cache_key

logger = logging.getLogger(__name__)


def _cache_path(cache_key: str):
    """Return (absolute_path, relative_url_path) for a given cache key."""
    from django_cfg.core.utils.cache import FileCache
    from django_cfg.modules.django_ogimage.cache._config import get_og_config

    cfg = get_og_config()
    return FileCache.sharded_paths(cache_key, cfg.media_subdir, suffix=".png")


def get_or_create_og_url(params: OGImageParams, request=None) -> str:
    """
    Return URL to the OG image for the given params.

    Renders and caches on first call. Instant on subsequent calls —
    no DB, no network, just a filesystem check.

    Cache path: MEDIA_ROOT/ogimage/<key[:2]>/<key[2:4]>/<key>.png

    Args:
        params:  OGImageParams instance.
        request: Django HttpRequest — if provided, returns an absolute URL.
                 If None, returns a relative URL path.

    Returns:
        URL string pointing to the PNG file.
    """
    cache_key = compute_cache_key(params)
    abs_path, rel_url = _cache_path(cache_key)

    if not abs_path.exists():
        from .renderer import render
        try:
            png_bytes = render(params)
        except Exception:
            logger.exception("OG image render failed for cache_key=%s", cache_key)
            raise

        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_bytes(png_bytes)
        logger.debug("OG image created: %s", abs_path)

    if request is not None:
        return request.build_absolute_uri(rel_url)
    return rel_url
