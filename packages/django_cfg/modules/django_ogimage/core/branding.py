"""
get_branded_og_url — convenience wrapper that adds logo + site_name branding.

Logo fetching happens here. SVG rasterization is delegated to .svg module.
The combined cache key covers params + branding + layout so each combination
is stored as a separate file.
"""
from __future__ import annotations

import hashlib
import json
import logging

from .icon import get_icon_path
from .layout import DEFAULT, OGLayoutPreset
from .params import OGImageParams, compute_cache_key
from .svg import _is_svg, _svg_to_png

logger = logging.getLogger(__name__)


def get_branded_og_url(
    params: OGImageParams,
    *,
    logo_url: str = "",
    icon: str = "",
    site_name: str = "",
    layout: OGLayoutPreset = DEFAULT,
    request=None,
) -> str:
    """Return URL to a branded OG image (logo + site_name overlay).

    Same caching semantics as get_or_create_og_url, but the cache key also
    covers logo_url, site_name, and layout so each combination is stored separately.

    Args:
        params:    OGImageParams instance (content, colors, locale, size).
        logo_url:  HTTP(S) URL or absolute filesystem path to a PNG or SVG logo.
                   If empty, no logo is drawn.
        icon:      Name of a built-in Material icon (e.g. "dashboard").
                   Ignored if logo_url is set. Use list_icons() to see available.
        site_name: Short label rendered next to the logo.
                   If empty, nothing is drawn.
        layout:    OGLayoutPreset controlling element placement. Defaults to DEFAULT.
        request:   Django HttpRequest — returns absolute URL when provided.

    Returns:
        URL string pointing to the cached PNG file.
    """
    from django_cfg.core.utils.paths import get_media_path, get_media_url
    from django_cfg.modules.django_ogimage.cache._config import get_og_config
    from .renderer import render

    # icon takes effect only when logo_url is absent
    effective_logo_url = logo_url or (str(get_icon_path(icon)) if icon else "")

    branding_data = json.dumps(
        {"logo_url": effective_logo_url, "site_name": site_name, "layout": layout.name},
        sort_keys=True,
        separators=(",", ":"),
    )
    cache_key = hashlib.sha256((compute_cache_key(params) + branding_data).encode()).hexdigest()[:40]

    cfg = get_og_config()
    shard_a, shard_b = cache_key[:2], cache_key[2:4]
    abs_path = get_media_path(cfg.media_subdir, shard_a, shard_b, f"{cache_key}.png")
    rel_url = get_media_url(cfg.media_subdir, shard_a, shard_b, f"{cache_key}.png")

    if not abs_path.exists():
        logo_bytes: bytes | None = _load_logo(effective_logo_url, size=layout.logo_size) if effective_logo_url else None
        try:
            png_bytes = render(params, logo_bytes=logo_bytes, site_name=site_name, layout=layout)
        except Exception:
            logger.exception("Branded OG render failed for cache_key=%s", cache_key)
            raise
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_bytes(png_bytes)
        logger.debug("Branded OG image created: %s", abs_path)

    if request is not None:
        return request.build_absolute_uri(rel_url)
    return rel_url


# ── Logo loading ──────────────────────────────────────────────────────────────

def _load_logo(logo_url: str, size: int = 128) -> bytes | None:
    """Fetch logo bytes from a URL or local path. Rasterizes SVG if needed.

    Returns None on any error so the render continues without a logo.
    """
    try:
        raw = _fetch_bytes(logo_url)
        return _svg_to_png(raw, size=size * 2) if _is_svg(raw) else raw  # 2× for sharpness
    except Exception:
        logger.warning("Failed to load logo from %r — skipping", logo_url, exc_info=True)
        return None


def _fetch_bytes(source: str) -> bytes:
    if source.startswith(("http://", "https://")):
        import httpx
        resp = httpx.get(source, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        return resp.content
    with open(source, "rb") as fh:
        return fh.read()
