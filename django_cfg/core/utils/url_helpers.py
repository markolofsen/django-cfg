"""
URL generation utilities for django-cfg.

Provides helper functions to generate URLs dynamically from site_url / api_url
configuration, including media file URL building.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _resolve_media_base(api_url: str, media_url: str) -> str:
    """
    Return an absolute base URL for media files.

    If *media_url* is already absolute (starts with http/https) it is used
    as-is.  Otherwise it is treated as a path relative to *api_url*.

    Examples::

        _resolve_media_base("https://api.ex.com", "/media/")
        → "https://api.ex.com/media/"

        _resolve_media_base("https://api.ex.com", "https://cdn.ex.com/media/")
        → "https://cdn.ex.com/media/"
    """
    if media_url.startswith(("http://", "https://")):
        return media_url.rstrip("/") + "/"
    return api_url.rstrip("/") + "/" + media_url.lstrip("/")


def build_media_url(
    path: Optional[str],
    *,
    api_url: str,
    media_url: str,
    fallback: Optional[str] = None,
) -> Optional[str]:
    """
    Build an absolute URL for a media file from its storage path.

    Args:
        path: Relative path as stored in the model field, e.g.
              ``"avatars/user_42.jpg"``.  If falsy, *fallback* is returned.
        api_url: Backend origin, e.g. ``"https://api.example.com"``.
        media_url: Django MEDIA_URL value — either a relative path
                   (``"/media/"``) or a fully-qualified CDN URL
                   (``"https://cdn.example.com/media/"``).
        fallback: Value returned when *path* is empty/None (default ``None``).

    Returns:
        Absolute URL string, or *fallback* if *path* is empty.

    Examples::

        build_media_url(
            "avatars/user_42.jpg",
            api_url="https://api.example.com",
            media_url="/media/",
        )
        → "https://api.example.com/media/avatars/user_42.jpg"

        build_media_url(
            "avatars/user_42.jpg",
            api_url="https://api.example.com",
            media_url="https://cdn.example.com/media/",
        )
        → "https://cdn.example.com/media/avatars/user_42.jpg"

        build_media_url(None, api_url="...", media_url="...")
        → None
    """
    if not path:
        return fallback

    base = _resolve_media_base(api_url, media_url)
    return base + path.lstrip("/")


def get_media_url(path: Optional[str], fallback: Optional[str] = None) -> Optional[str]:
    """
    Build an absolute media URL using the current django-cfg config.

    Reads ``config.api_url`` and ``config.media_url`` from the active config
    at call time — safe to use anywhere Django settings are loaded.

    Args:
        path: Relative path stored in a model field (e.g. ``"avatars/x.jpg"``).
        fallback: Returned when *path* is empty or config is unavailable.

    Returns:
        Absolute URL string, or *fallback*.

    Example::

        from django_cfg.core.utils.url_helpers import get_media_url

        avatar_url = get_media_url(user.avatar)   # → "https://api.ex.com/media/avatars/x.jpg"
        logo_url   = get_media_url(org.logo, fallback="/static/default-logo.png")
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if config is None:
            logger.warning("get_media_url: no active config, returning fallback")
            return fallback
        return build_media_url(path, api_url=config.api_url, media_url=config.media_url)
    except Exception as e:
        logger.warning(f"get_media_url: could not build URL: {e}")
        return fallback


def get_ticket_url(ticket_uuid: str, fallback: str = "#ticket") -> str:
    """
    Generate support ticket URL on the fly from site_url.

    Args:
        ticket_uuid: UUID of the support ticket
        fallback: Fallback URL if config is not available (default: "#ticket")

    Returns:
        Complete URL to the ticket

    Example:
        >>> get_ticket_url("abc-123-def")
        "https://yoursite.com/support/ticket/abc-123-def"
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()

        if config and hasattr(config, 'site_url'):
            return f"{config.site_url}/support/ticket/{ticket_uuid}"
        else:
            logger.warning("Config or site_url not available for ticket URL generation")
            return f"{fallback}-{ticket_uuid}"

    except Exception as e:
        logger.warning(f"Could not generate ticket URL: {e}")
        return f"{fallback}-{ticket_uuid}"


def get_otp_url(otp_code: str, fallback: str = "#otp") -> str:
    """
    Generate OTP verification URL on the fly from site_url.

    Args:
        otp_code: OTP verification code
        fallback: Fallback URL if config is not available (default: "#otp")

    Returns:
        Complete URL to the OTP verification page

    Example:
        >>> get_otp_url("123456")
        "https://yoursite.com/auth/?otp=123456"
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()

        if config and hasattr(config, 'site_url'):
            return f"{config.site_url}/auth/?otp={otp_code}"
        else:
            logger.warning("Config or site_url not available for OTP URL generation")
            return f"{fallback}-{otp_code}"

    except Exception as e:
        logger.warning(f"Could not generate OTP URL: {e}")
        return f"{fallback}-{otp_code}"


def build_api_url(path: str, *, api_url: str) -> str:
    """
    Build an absolute URL relative to *api_url*.

    Args:
        path: URL path segment, e.g. ``"apix/catalog_photos/photo/abc.jpg"``.
        api_url: Backend origin, e.g. ``"https://api.example.com"``.

    Returns:
        Absolute URL string.

    Examples::

        build_api_url("apix/catalog/photo/abc.jpg", api_url="https://api.example.com")
        → "https://api.example.com/apix/catalog/photo/abc.jpg"
    """
    return f"{api_url.rstrip('/')}/{path.lstrip('/')}"


def get_api_url(path: str, fallback: Optional[str] = None) -> Optional[str]:
    """
    Build an absolute URL relative to the current config's *api_url*.

    Reads ``config.api_url`` from the active config at call time.

    Args:
        path: URL path segment, e.g. ``"apix/catalog_photos/photo/abc.jpg"``.
        fallback: Returned when config is unavailable.

    Returns:
        Absolute URL string, or *fallback*.

    Example::

        from django_cfg.core.utils.url_helpers import get_api_url

        url = get_api_url(f"apix/catalog_photos/photo/{photo_id}.jpg")
        # → "https://api.example.com/apix/catalog_photos/photo/<uuid>.jpg"
    """
    try:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if config is None:
            logger.warning("get_api_url: no active config, returning fallback")
            return fallback
        return build_api_url(path, api_url=config.api_url)
    except Exception as e:
        logger.warning(f"get_api_url: could not build URL: {e}")
        return fallback


__all__ = ["get_ticket_url", "get_otp_url", "get_media_url", "build_media_url", "build_api_url", "get_api_url"]
