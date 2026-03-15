"""
Schema Generation Utilities.

Handles OpenAPI schema generation from Django.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django_cfg.modules.django_client.core.ir import IRContext


class SchemaUtils:
    """
    Utilities for OpenAPI schema operations.

    Handles:
    - Generating OpenAPI schema from Django
    - Parsing to IR
    - Saving schema files
    """

    @staticmethod
    def generate_openapi_schema(
        urlconf_module: Any,
        title: str,
        description: str | None = None,
        version: str = "1.0.0",
    ) -> dict:
        """
        Generate OpenAPI schema from Django URLconf.

        Args:
            urlconf_module: Django URLconf module
            title: API title
            description: API description
            version: API version

        Returns:
            OpenAPI schema dict
        """
        from django.conf import settings
        from drf_spectacular.generators import SchemaGenerator

        # Temporarily patch settings for proper schema generation
        original_settings = getattr(settings, 'SPECTACULAR_SETTINGS', {}).copy()
        patched_settings = original_settings.copy()
        patched_settings['COMPONENT_SPLIT_REQUEST'] = True
        patched_settings['COMPONENT_SPLIT_PATCH'] = True
        settings.SPECTACULAR_SETTINGS = patched_settings

        try:
            generator = SchemaGenerator(
                title=title,
                description=description,
                version=version,
                urlconf=urlconf_module,
            )
            schema_dict = generator.get_schema(request=None, public=True)
            return schema_dict
        finally:
            settings.SPECTACULAR_SETTINGS = original_settings

    @staticmethod
    def add_django_metadata(
        schema: dict,
        group_name: str,
        app_labels: list[str],
    ) -> dict:
        """Add Django-specific metadata to schema."""
        schema.setdefault('info', {}).setdefault('x-django-metadata', {
            'group': group_name,
            'apps': app_labels,
            'generator': 'django-client',
            'generator_version': '1.0.0',
        })
        return schema

    @staticmethod
    def save_schema(schema: dict, path: Path) -> None:
        """Save schema to JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(schema, f, indent=2)

    @staticmethod
    def parse_to_ir(schema: dict) -> "IRContext":
        """Parse OpenAPI schema to IR."""
        from django_cfg.modules.django_client.core import parse_openapi
        return parse_openapi(schema)


__all__ = ["SchemaUtils"]
