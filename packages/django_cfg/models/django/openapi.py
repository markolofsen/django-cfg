"""
Django Client (OpenAPI) Configuration with DRF Integration

Extended configuration model that integrates openapi_client for automatic
TypeScript and Python client generation from Django REST Framework endpoints.

This replaces django-revolution with a cleaner, faster, type-safe implementation.
"""

from typing import Any, Dict, Optional

from pydantic import Field

from django_cfg.modules.django_client.core.config import OpenAPIConfig, OpenAPIGroupConfig


class OpenAPIClientConfig(OpenAPIConfig):
    """
    Extended OpenAPI configuration with DRF parameters for django-cfg integration.

    This extends the base OpenAPIConfig to include DRF-specific
    parameters and django-cfg integration helpers.

    Example:
        ```python
        from django_cfg import OpenAPIClientConfig, OpenAPIGroupConfig

        config = OpenAPIClientConfig(
            enabled=True,
            groups=[
                OpenAPIGroupConfig(
                    name='api',
                    apps=['users', 'posts'],
                    title='Main API',
                    version='v1',
                ),
            ],
            drf_title='My API',
            drf_description='REST API for my project',
        )
        ```
    """

    # DRF Configuration parameters for automatic DRF setup
    drf_title: str = Field(
        default="API",
        description="API title for DRF Spectacular"
    )
    drf_description: str = Field(
        default="RESTful API",
        description="API description for DRF Spectacular"
    )
    drf_version: str = Field(
        default="1.0.0",
        description="API version for DRF Spectacular"
    )
    drf_schema_path_prefix: Optional[str] = Field(
        default=None,  # Will default to "/api/" if None
        description="Schema path prefix for DRF Spectacular"
    )
    drf_enable_browsable_api: bool = Field(
        default=True,
        description="Enable DRF browsable API with Tailwind theme"
    )
    drf_enable_throttling: bool = Field(
        default=False,
        description="Enable DRF throttling"
    )
    drf_serve_include_schema: bool = Field(
        default=False,
        description="Include schema in Spectacular UI"
    )

    # Django-cfg specific integration
    api_prefix: str = Field(
        default="api",
        description="API prefix for URL routing (e.g., 'api' -> /api/...)"
    )

    def get_drf_schema_path_prefix(self) -> str:
        """Get the schema path prefix, defaulting to api_prefix if not set."""
        if self.drf_schema_path_prefix:
            return self.drf_schema_path_prefix
        return f"/{self.api_prefix}/"

    def get_drf_config_kwargs(self) -> Dict[str, Any]:
        """
        Get kwargs for DRF configuration from this config.

        Returns:
            Dict of parameters for DRF + Spectacular setup
        """
        return {
            "title": self.drf_title,
            "description": self.drf_description,
            "version": self.drf_version,
            "schema_path_prefix": self.get_drf_schema_path_prefix(),
            "enable_browsable_api": self.drf_enable_browsable_api,
            "enable_throttling": self.drf_enable_throttling,
            "serve_include_schema": self.drf_serve_include_schema,
            # REQUIRED by django-client for correct Request/Response split
            "component_split_request": True,
            "component_split_patch": True,
        }

    def get_groups_with_defaults(self) -> Dict[str, OpenAPIGroupConfig]:
        """
        Get groups as a dictionary.

        Returns:
            Dict of groups from configuration
        """
        # Convert list to dict for compatibility
        return {group.name: group for group in self.groups}

