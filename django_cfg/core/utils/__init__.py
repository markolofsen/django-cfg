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

__all__ = [
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
