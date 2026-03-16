"""
Project path helpers for django-cfg modules.

All functions read Django settings lazily at call time — safe to import at
module level even before Django is fully configured.

These are the canonical runtime paths for all djangocfg-based projects:

    BASE_DIR/
        static/         ← source static files (STATICFILES_DIRS)
        staticfiles/    ← collected static files (STATIC_ROOT)
        media/          ← user uploads (MEDIA_ROOT)
        templates/      ← Django templates
        logs/           ← application logs

Usage::

    from django_cfg.core.utils.paths import (
        get_base_path,
        get_static_root, get_static_url,
        get_media_path, get_media_url,
        get_logs_path, get_templates_path,
    )

    get_media_path("ogimage", "ab", "cd", "abcdef.png")
    # → /project/media/ogimage/ab/cd/abcdef.png

    get_static_root("css", "main.css")
    # → /project/staticfiles/css/main.css

    get_base_path("openapi", "clients", "typescript")
    # → /project/openapi/clients/typescript
"""
from __future__ import annotations

from pathlib import Path


def get_base_path(*parts: str) -> Path:
    """Return ``BASE_DIR / parts`` — absolute path from project root."""
    from django.conf import settings
    base = Path(settings.BASE_DIR)
    return base.joinpath(*parts) if parts else base


def get_static_root(*parts: str) -> Path:
    """Return ``STATIC_ROOT / parts`` — collected static files directory."""
    from django.conf import settings
    root = Path(settings.STATIC_ROOT)
    return root.joinpath(*parts) if parts else root


def get_static_url(*parts: str) -> str:
    """Return ``STATIC_URL/parts`` — URL for static files."""
    from django.conf import settings
    base = settings.STATIC_URL.rstrip("/")
    if not parts:
        return base + "/"
    return base + "/" + "/".join(parts)


def get_media_path(*parts: str) -> Path:
    """Return ``MEDIA_ROOT / parts`` — absolute path inside the media directory."""
    from django.conf import settings
    root = Path(settings.MEDIA_ROOT)
    return root.joinpath(*parts) if parts else root


def get_media_url(*parts: str) -> str:
    """Return ``MEDIA_URL/parts`` — relative URL inside the media directory."""
    from django.conf import settings
    base = settings.MEDIA_URL.rstrip("/")
    if not parts:
        return base + "/"
    return base + "/" + "/".join(parts)


def get_logs_path(*parts: str) -> Path:
    """Return ``BASE_DIR/logs / parts`` — application logs directory."""
    from django.conf import settings
    root = Path(settings.BASE_DIR) / "logs"
    return root.joinpath(*parts) if parts else root


def get_templates_path(*parts: str) -> Path:
    """Return ``BASE_DIR/templates / parts`` — templates directory."""
    from django.conf import settings
    root = Path(settings.BASE_DIR) / "templates"
    return root.joinpath(*parts) if parts else root


__all__ = [
    "get_base_path",
    "get_static_root",
    "get_static_url",
    "get_media_path",
    "get_media_url",
    "get_logs_path",
    "get_templates_path",
]
