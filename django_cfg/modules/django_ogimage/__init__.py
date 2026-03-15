"""django_ogimage — OG image generation module for djangocfg.

Renders OG images on the fly using PicTex (with Pillow fallback).
Caches PNG files in MEDIA_ROOT/ogimage/<key[:2]>/<key[2:4]>/<key>.png.

Quick start::

    from django_cfg.modules.django_ogimage import get_or_create_og_url, OGImageParams
    from django_cfg.modules.django_ogimage.presets import DARK_BLUE

    url = get_or_create_og_url(
        DARK_BLUE.to_params(title=obj.title, description=obj.excerpt),
        request=request,
    )

Branded (logo + site_name)::

    from django_cfg.modules.django_ogimage import get_branded_og_url, HERO

    url = get_branded_og_url(
        DARK_BLUE.to_params(title=obj.title),
        logo_url="https://example.com/logo.svg",
        site_name="MySite",
        layout=HERO,
        request=request,
    )
"""
from .core.fonts import prefetch_all as _prefetch_fonts
import sys as _sys
if "pytest" not in _sys.modules:
    _prefetch_fonts()
del _sys, _prefetch_fonts
from .core.branding import get_branded_og_url
from .core.icon import get_icon_path, list_icons
from .core.layout import (
    ALL as LAYOUTS,
    ARTICLE,
    DEFAULT,
    HERO,
    MINIMAL,
    OGLayoutPreset,
    corner_to_fixed_pos,
    get_layout,
)
from .core.params import OGImageParams, compute_cache_key
from .core.renderer import render
from .core.service import get_or_create_og_url
from .http.utils import build_og_url
from .presets import (
    ALL,
    DARK,
    DARK_BLUE,
    DARK_GREEN,
    DARK_PURPLE,
    DARK_ROSE,
    LIGHT,
    LIGHT_GRAY,
    LIGHT_GREEN,
    LIGHT_WARM,
    OGImagePreset,
    build_preset,
    get_preset,
)

__all__ = [
    # params
    "OGImageParams",
    "compute_cache_key",
    # icons
    "get_icon_path",
    "list_icons",
    # rendering
    "render",
    "get_or_create_og_url",
    "get_branded_og_url",
    "build_og_url",
    # layouts
    "OGLayoutPreset",
    "DEFAULT",
    "HERO",
    "ARTICLE",
    "MINIMAL",
    "LAYOUTS",
    "get_layout",
    "corner_to_fixed_pos",
    # color presets
    "OGImagePreset",
    "ALL",
    "get_preset",
    "build_preset",
    "DARK",
    "DARK_BLUE",
    "DARK_PURPLE",
    "DARK_GREEN",
    "DARK_ROSE",
    "LIGHT",
    "LIGHT_GRAY",
    "LIGHT_WARM",
    "LIGHT_GREEN",
]
