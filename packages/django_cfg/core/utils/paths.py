"""
Project path helpers for django-cfg modules.

All functions read Django settings lazily at call time — safe to import at
module level even before Django is fully configured.

Usage::

    from django_cfg.core.utils.paths import get_media_path, get_media_url, get_base_path

    # MEDIA_ROOT/ogimage/ab/cd/abcdef....png
    path = get_media_path("ogimage", "ab", "cd", "abcdef.png")

    # /media/ogimage/ab/cd/abcdef....png
    url = get_media_url("ogimage", "ab", "cd", "abcdef.png")

    # BASE_DIR/openapi/clients/typescript
    path = get_base_path("openapi", "clients", "typescript")
"""
from __future__ import annotations

from pathlib import Path


def get_base_path(*parts: str) -> Path:
    """Return ``BASE_DIR / parts`` — absolute path from project root.

    ``BASE_DIR`` is resolved via ``settings.BASE_DIR`` (set by DjangoConfig
    to the directory containing ``manage.py``).

    Args:
        *parts: Path components to join after ``BASE_DIR``.

    Returns:
        Absolute :class:`~pathlib.Path`.

    Example::

        get_base_path("openapi", "clients")
        # → /project/openapi/clients
    """
    from django.conf import settings
    base = Path(settings.BASE_DIR)
    return base.joinpath(*parts) if parts else base


def get_media_path(*parts: str) -> Path:
    """Return ``MEDIA_ROOT / parts`` — absolute path inside the media directory.

    Args:
        *parts: Path components to join after ``MEDIA_ROOT``.

    Returns:
        Absolute :class:`~pathlib.Path`.

    Example::

        get_media_path("ogimage", "ab", "cd", "abcdef.png")
        # → /project/media/ogimage/ab/cd/abcdef.png
    """
    from django.conf import settings
    root = Path(settings.MEDIA_ROOT)
    return root.joinpath(*parts) if parts else root


def get_media_url(*parts: str) -> str:
    """Return ``MEDIA_URL/parts`` — relative URL inside the media directory.

    Handles trailing/leading slashes correctly regardless of how ``MEDIA_URL``
    is configured.

    Args:
        *parts: URL path components to join after ``MEDIA_URL``.

    Returns:
        URL string starting with ``/``.

    Example::

        get_media_url("ogimage", "ab", "cd", "abcdef.png")
        # → /media/ogimage/ab/cd/abcdef.png
    """
    from django.conf import settings
    base = settings.MEDIA_URL.rstrip("/")
    if not parts:
        return base + "/"
    return base + "/" + "/".join(parts)


__all__ = ["get_base_path", "get_media_path", "get_media_url"]
