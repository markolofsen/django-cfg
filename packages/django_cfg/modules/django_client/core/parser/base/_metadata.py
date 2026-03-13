"""
Metadata parsing mixin — OpenAPI info and Django/drf-spectacular settings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...ir import DjangoGlobalMetadata, OpenAPIInfo

if TYPE_CHECKING:
    from ..models import OpenAPISpec
    from ._protocol import ParserState


# ---------------------------------------------------------------------------
# Pure helpers — independently testable without a parser instance
# ---------------------------------------------------------------------------

def _detect_split_request(spec: OpenAPISpec) -> bool:
    """Return True if the spec contains paired FooRequest / Foo schemas."""
    if not spec.components or not spec.components.schemas:
        return False
    names = set(spec.components.schemas.keys())
    return any(n.endswith("Request") and n[:-7] in names for n in names)


def _detect_split_patch(spec: OpenAPISpec) -> bool:
    """Return True if the spec contains paired PatchedFoo / Foo schemas."""
    if not spec.components or not spec.components.schemas:
        return False
    names = set(spec.components.schemas.keys())
    return any(n.startswith("Patched") and n[7:] in names for n in names)


# ---------------------------------------------------------------------------
# Mixin
# ---------------------------------------------------------------------------

class MetadataParserMixin:
    """Parses OpenAPI info block and Django metadata (SPECTACULAR_SETTINGS, auth classes)."""

    def _parse_openapi_info(self: ParserState) -> OpenAPIInfo:
        info = self.spec.info
        return OpenAPIInfo(
            version=self.spec.normalized_version,
            title=info.title,
            description=info.description,
            api_version=info.version,
            servers=self.spec.server_urls,
            contact_name=info.contact.name if info.contact else None,
            contact_email=info.contact.email if info.contact else None,
            license_name=info.license.name if info.license else None,
            license_url=info.license.url if info.license else None,
        )

    def _parse_django_metadata(self: ParserState) -> DjangoGlobalMetadata:
        has_split = self._get_django_spectacular_setting('COMPONENT_SPLIT_REQUEST')
        has_patch = self._get_django_spectacular_setting('COMPONENT_SPLIT_PATCH')

        if has_split is None:
            has_split = _detect_split_request(self.spec)
        if has_patch is None:
            has_patch = _detect_split_patch(self.spec)

        auth_classes = self._get_drf_authentication_classes()

        return DjangoGlobalMetadata(
            component_split_request=has_split if has_split is not None else False,
            component_split_patch=has_patch if has_patch is not None else False,
            oas_version=self.spec.normalized_version,
            default_authentication_classes=auth_classes,
        )

    def _get_django_spectacular_setting(self, setting_name: str) -> bool | None:
        try:
            from django.conf import settings
            if not settings.configured:
                return None
            spectacular_settings = getattr(settings, 'SPECTACULAR_SETTINGS', {})
            return spectacular_settings.get(setting_name)
        except ImportError:
            return None
        except Exception:
            return None

    def _get_drf_authentication_classes(self) -> list[str]:
        try:
            from django.conf import settings
            if not settings.configured:
                return []
            rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
            auth_classes = rest_framework.get('DEFAULT_AUTHENTICATION_CLASSES', [])
            if isinstance(auth_classes, (list, tuple)):
                return list(auth_classes)
            return []
        except ImportError:
            return []
        except Exception:
            return []
