"""URL patterns for OpenAPI schema + Swagger UI.

Lazy-evaluated: defer DRF/drf-spectacular import until Django is configured,
otherwise api_settings caches with the wrong DEFAULT_SCHEMA_CLASS.
"""

from __future__ import annotations

from typing import Any


def _is_django_configured() -> bool:
    try:
        from django.conf import settings

        return bool(settings.configured)
    except ImportError:
        return False


def get_openapi_urls() -> list[Any]:
    """Return URL patterns for each configured group.

    Pattern shape: `/{group_name}/schema/` → JSON schema (drf-spectacular).
    """
    try:
        from django.urls import path
        from drf_spectacular.views import SpectacularAPIView

        from .openapi.service import (
            get_openapi_service,
        )
    except ImportError:
        return []

    service = get_openapi_service()
    if not service.config or not service.is_enabled():
        return []

    patterns: list[Any] = []
    for group in service.list_groups():
        urlconf_name = f"_django_generator_urlconf_{group.name}"
        patterns.append(
            path(
                f"{group.name}/schema/",
                SpectacularAPIView.as_view(
                    urlconf=urlconf_name,
                    api_version=group.version,
                ),
                name=f"openapi-schema-{group.name}",
            )
        )
    return patterns


class _LazyURLPatterns:
    """Iterable+indexable patterns proxy that only resolves on access."""

    def __init__(self) -> None:
        self._patterns: list[Any] | None = None

    def _resolve(self) -> list[Any]:
        if self._patterns is None:
            self._patterns = get_openapi_urls() if _is_django_configured() else []
        return self._patterns

    def __iter__(self):
        return iter(self._resolve())

    def __getitem__(self, index):
        return self._resolve()[index]

    def __len__(self) -> int:
        return len(self._resolve())

    def clear(self) -> None:
        self._resolve().clear()

    def extend(self, items: list[Any]) -> None:
        self._resolve().extend(items)


urlpatterns = _LazyURLPatterns()


__all__ = ["get_openapi_urls", "urlpatterns"]
