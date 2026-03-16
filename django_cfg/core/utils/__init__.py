"""Core utilities for django-cfg."""

from .cache import CacheKey, FileCache, LazyFileResource
from .paths import (
    get_base_path,
    get_static_root,
    get_static_url,
    get_media_path,
    get_media_url,
    get_logs_path,
    get_templates_path,
)
from .url_helpers import get_otp_url, get_ticket_url

__all__ = [
    "get_ticket_url",
    "get_otp_url",
    "get_base_path",
    "get_static_root",
    "get_static_url",
    "get_media_path",
    "get_media_url",
    "get_logs_path",
    "get_templates_path",
    "CacheKey",
    "FileCache",
    "LazyFileResource",
]
