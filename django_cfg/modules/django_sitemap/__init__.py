"""django_sitemap — reusable sitemap source registry + JSON feed.

Apps declare URL sources in `sitemap_sources.py`; the module exposes a
typed JSON contract that Next.js (or any other consumer) turns into
search-engine-ready XML.

See `@plans/plan13-sitemap/` in the carapis project for the full design.
"""
from __future__ import annotations

default_app_config = "django_cfg.modules.django_sitemap.apps.SitemapAppConfig"

from .config import SitemapConfig, get_sitemap_config, set_sitemap_config
from .registry import all_sources, get, register
from .sources import SitemapSource, resolve_field

__all__ = [
    "SitemapConfig",
    "SitemapSource",
    "all_sources",
    "get",
    "get_sitemap_config",
    "register",
    "resolve_field",
    "set_sitemap_config",
]
