"""
DRF Spectacular configuration for OpenAPI/Swagger documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .redoc import RedocUISettings
from .swagger import SwaggerUISettings


class SpectacularConfig(BaseModel):
    """
    📚 Spectacular Configuration

    Handles DRF Spectacular settings for OpenAPI/Swagger documentation.
    """

    # API Information
    title: str = Field(default="API Documentation", description="API title")
    description: str = Field(default="RESTful API with modern architecture", description="API description")
    version: str = Field(default="1.0.0", description="API version")
    terms_of_service: Optional[str] = Field(
        default=None, description="Terms of service URL"
    )

    # Contact Information
    contact_name: Optional[str] = Field(default=None, description="Contact name")
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    contact_url: Optional[str] = Field(default=None, description="Contact URL")

    # License Information
    license_name: Optional[str] = Field(default=None, description="License name")
    license_url: Optional[str] = Field(default=None, description="License URL")

    # Schema Settings
    schema_path_prefix: str = Field(default="/api", description="Schema path prefix")
    serve_include_schema: bool = Field(default=False, description="Include schema in UI")
    component_split_request: bool = Field(default=True, description="Split request components")
    sort_operations: bool = Field(default=False, description="Sort operations")

    # UI Settings
    swagger_ui_settings: SwaggerUISettings = Field(
        default_factory=SwaggerUISettings, description="Swagger UI settings"
    )
    redoc_ui_settings: RedocUISettings = Field(
        default_factory=RedocUISettings, description="Redoc UI settings"
    )

    # Post-processing
    postprocessing_hooks: List[str] = Field(
        default_factory=lambda: [
            'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields'
        ],
        description="Post-processing hooks"
    )

    # NOTE: Enum generation settings are handled by django-client (OpenAPI)
    # Only override if you need different values than django-client defaults

    # Enum overrides
    enum_name_overrides: Dict[str, str] = Field(
        default_factory=lambda: {
            'ValidationErrorEnum': 'django.contrib.auth.models.ValidationError',
        },
        description="Enum name overrides"
    )

    def get_spectacular_settings(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get django-cfg Spectacular extensions.

        NOTE: This extends django-client's base settings, not replaces them.
        Only include settings that are unique to django-cfg or critical fixes.

        Args:
            project_name: Project name from DjangoConfig to use as API title
        """
        settings = {
            # django-cfg specific UI enhancements
            "REDOC_UI_SETTINGS": self.redoc_ui_settings.to_dict(),  # django-client doesn't have custom Redoc settings

            # django-cfg specific processing extensions
            "ENUM_NAME_OVERRIDES": self.enum_name_overrides,  # Custom enum overrides

            # CRITICAL: Ensure enum generation is always enabled (fix django-client gaps)
            # These settings ensure proper enum generation even if django-client config changes
            "GENERATE_ENUM_FROM_CHOICES": True,
            "ENUM_GENERATE_CHOICE_FROM_PATH": True,
            "ENUM_NAME_SUFFIX": "Enum",
            "CAMELIZE_NAMES": False,
            "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
        }

        # Use project_name as API title if provided and title is default
        if project_name and self.title == "API Documentation":
            settings["TITLE"] = f"{project_name} API"
        elif self.title != "API Documentation":
            settings["TITLE"] = self.title

        # Always set description and version
        settings["DESCRIPTION"] = self.description
        settings["VERSION"] = self.version

        # Add optional fields if present
        if self.terms_of_service:
            settings["TERMS_OF_SERVICE"] = self.terms_of_service

        # Contact information
        if any([self.contact_name, self.contact_email, self.contact_url]):
            settings["CONTACT"] = {}
            if self.contact_name:
                settings["CONTACT"]["name"] = self.contact_name
            if self.contact_email:
                settings["CONTACT"]["email"] = self.contact_email
            if self.contact_url:
                settings["CONTACT"]["url"] = self.contact_url

        # License information
        if self.license_name:
            settings["LICENSE"] = {"name": self.license_name}
            if self.license_url:
                settings["LICENSE"]["url"] = self.license_url

        return settings


__all__ = [
    "SpectacularConfig",
]
