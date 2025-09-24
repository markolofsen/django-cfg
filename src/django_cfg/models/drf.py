"""
Django REST Framework Configuration Models

Handles DRF and DRF Spectacular settings with Pydantic models.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class SwaggerUISettings(BaseModel):
    """Swagger UI specific settings."""

    try_it_out_enabled: bool = Field(
        default=True, description="Enable Try It Out feature"
    )
    doc_expansion: str = Field(
        default="list", description="Default expansion setting (list, full, none)"
    )
    deep_linking: bool = Field(default=True, description="Enable deep linking")
    persist_authorization: bool = Field(
        default=True, description="Persist authorization data"
    )
    display_operation_id: bool = Field(
        default=True, description="Display operation IDs"
    )
    default_models_expand_depth: int = Field(
        default=1, description="Default expansion depth for models"
    )
    default_model_expand_depth: int = Field(
        default=1, description="Default expansion depth for model"
    )
    default_model_rendering: str = Field(
        default="model", description="Default model rendering"
    )
    filter: bool = Field(default=True, description="Enable filtering")
    show_extensions: bool = Field(default=False, description="Show extensions")
    show_common_extensions: bool = Field(
        default=True, description="Show common extensions"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Swagger UI."""
        return {
            "tryItOutEnabled": self.try_it_out_enabled,
            "docExpansion": self.doc_expansion,
            "deepLinking": self.deep_linking,
            "persistAuthorization": self.persist_authorization,
            "displayOperationId": self.display_operation_id,
            "defaultModelsExpandDepth": self.default_models_expand_depth,
            "defaultModelExpandDepth": self.default_model_expand_depth,
            "defaultModelRendering": self.default_model_rendering,
            "filter": self.filter,
            "showExtensions": self.show_extensions,
            "showCommonExtensions": self.show_common_extensions,
        }


class RedocUISettings(BaseModel):
    """Redoc UI specific settings."""
    
    native_scrollbars: bool = Field(default=True, description="Use native scrollbars")
    theme_color: str = Field(default="#7c3aed", description="Primary theme color")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redoc UI."""
        return {
            "nativeScrollbars": self.native_scrollbars,
            "theme": {
                "colors": {
                    "primary": {
                        "main": self.theme_color
                    }
                }
            }
        }


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
    
    # NOTE: Enum generation settings are handled by django-revolution
    # Only override if you need different values than Revolution defaults
    
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
        
        NOTE: This extends Revolution's base settings, not replaces them.
        Only include settings that are unique to django-cfg or critical fixes.
        
        Args:
            project_name: Project name from DjangoConfig to use as API title
        """
        settings = {
            # django-cfg specific UI enhancements
            "REDOC_UI_SETTINGS": self.redoc_ui_settings.to_dict(),  # Revolution doesn't have custom Redoc settings
            
            # django-cfg specific processing extensions
            "ENUM_NAME_OVERRIDES": self.enum_name_overrides,  # Custom enum overrides
            
            # CRITICAL: Ensure enum generation is always enabled (fix Revolution gaps)
            # These settings ensure proper enum generation even if Revolution config changes
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


class DRFConfig(BaseModel):
    """
    🔧 Django REST Framework Configuration
    
    Handles REST Framework settings with sensible defaults.
    """
    
    # Authentication
    authentication_classes: List[str] = Field(
        default_factory=lambda: [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        description="Default authentication classes"
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
    
    def get_rest_framework_settings(self) -> Dict[str, Any]:
        """Get complete REST Framework settings."""
        return {
            'DEFAULT_AUTHENTICATION_CLASSES': self.authentication_classes,
            'DEFAULT_PERMISSION_CLASSES': self.permission_classes,
            'DEFAULT_PAGINATION_CLASS': self.pagination_class,
            'PAGE_SIZE': self.page_size,
            'DEFAULT_SCHEMA_CLASS': self.schema_class,
            'DEFAULT_THROTTLE_CLASSES': self.throttle_classes,
            'DEFAULT_THROTTLE_RATES': self.throttle_rates,
            'DEFAULT_VERSIONING_CLASS': self.versioning_class,
            'DEFAULT_VERSION': self.default_version,
            'ALLOWED_VERSIONS': self.allowed_versions,
        }
