"""
Django REST Framework configuration.
"""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class DRFConfig(BaseModel):
    """
    🔧 Django REST Framework Configuration

    Handles REST Framework settings with sensible defaults.
    """

    # Authentication
    authentication_classes: List[str] = Field(
        default_factory=lambda: [
            'django_cfg.middleware.authentication.JWTAuthenticationWithLastLogin',
            'rest_framework.authentication.TokenAuthentication',
            # SessionAuthentication removed from defaults (requires CSRF)
            # Add it manually in your config if you need Browsable API with session auth
        ],
        description="Default authentication classes (JWT with auto last_login update)"
    )

    # Permissions
    permission_classes: List[str] = Field(
        default_factory=lambda: [
            'rest_framework.permissions.IsAuthenticated',
        ],
        description="Default permission classes"
    )

    # Pagination
    pagination_class: str = Field(
        default='django_cfg.middleware.pagination.DefaultPagination',
        description="Default pagination class"
    )
    page_size: int = Field(default=100, description="Default page size")

    # Schema
    schema_class: str = Field(
        default='drf_spectacular.openapi.AutoSchema',
        description="Default schema class"
    )

    # Throttling
    throttle_classes: List[str] = Field(
        default_factory=lambda: [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle'
        ],
        description="Default throttle classes"
    )
    throttle_rates: Dict[str, str] = Field(
        default_factory=lambda: {
            'anon': '200/hour',
            'user': '2000/hour'
        },
        description="Default throttle rates"
    )

    # Versioning
    versioning_class: str = Field(
        default='rest_framework.versioning.NamespaceVersioning',
        description="Default versioning class"
    )
    default_version: str = Field(default='v1', description="Default API version")
    allowed_versions: List[str] = Field(
        default_factory=lambda: ['v1'],
        description="Allowed API versions"
    )

    # Renderers
    renderer_classes: List[str] = Field(
        default_factory=lambda: [
            'rest_framework.renderers.JSONRenderer',
            'django_cfg.modules.django_drf_theme.renderers.TailwindBrowsableAPIRenderer',
        ],
        description="Default renderer classes (JSON + Tailwind Browsable API)"
    )

    def get_rest_framework_settings(self) -> Dict[str, Any]:
        """Get complete REST Framework settings."""
        return {
            'DEFAULT_AUTHENTICATION_CLASSES': self.authentication_classes,
            'DEFAULT_PERMISSION_CLASSES': self.permission_classes,
            'DEFAULT_RENDERER_CLASSES': self.renderer_classes,
            'DEFAULT_PAGINATION_CLASS': self.pagination_class,
            'PAGE_SIZE': self.page_size,
            'DEFAULT_SCHEMA_CLASS': self.schema_class,
            'DEFAULT_THROTTLE_CLASSES': self.throttle_classes,
            'DEFAULT_THROTTLE_RATES': self.throttle_rates,
            'DEFAULT_VERSIONING_CLASS': self.versioning_class,
            'DEFAULT_VERSION': self.default_version,
            'ALLOWED_VERSIONS': self.allowed_versions,
        }


__all__ = [
    "DRFConfig",
]
