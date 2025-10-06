"""
Django Revolution Core Configuration

Unified configuration system with comprehensive settings for stable generation.
Rich configuration options with smart defaults and validation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    pass

try:
    from django.conf import settings as django_settings
except ImportError:
    django_settings = None


class BaseCfgAutoModule(ABC):
    """
    Base class for all django-revolution auto-configuration modules.
    
    Provides unified configuration access and smart defaults.
    Inspired by django-cfg pattern.
    """
    
    def __init__(self, config: Optional[Any] = None):
        """Initialize the auto-configuration module."""
        self._config = config
    
    def set_config(self, config: Any) -> None:
        """Set the configuration instance."""
        self._config = config
    
    def get_config(self) -> Optional[Any]:
        """Get the current configuration instance."""
        return self._config
    
    def has_config_field(self, field_name: str) -> bool:
        """Check if config has a specific field with a non-None value."""
        if not self._config:
            return False
        return hasattr(self._config, field_name) and getattr(self._config, field_name) is not None
    
    def get_config_field(self, field_name: str, default=None):
        """Get a field value from config with fallback."""
        if not self._config:
            return default
        return getattr(self._config, field_name, default)
    
    @abstractmethod
    def get_smart_defaults(self):
        """Get smart default configuration for this module."""
        pass
    
    @abstractmethod
    def get_module_config(self):
        """Get the final configuration for this module."""
        pass


class ZoneConfig(BaseModel):
    """Zone configuration for API generation with comprehensive options."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    apps: List[str] = Field(..., description="List of Django apps in this zone")
    title: str = Field(..., description="Zone title")
    description: str = Field(..., description="Zone description")
    public: bool = Field(True, description="Is zone public")
    auth_required: bool = Field(False, description="Authentication required")
    version: str = Field("v1", description="API version")
    
    # Advanced zone settings for stability
    rate_limit: Optional[str] = Field(None, description="Rate limit configuration")
    permissions: Optional[List[str]] = Field(None, description="Required permissions")
    cors_enabled: bool = Field(False, description="Enable CORS for this zone")
    middleware: Optional[List[str]] = Field(None, description="Custom middleware")
    path_prefix: Optional[str] = Field(None, description="Path prefix for URLs")
    
    # Schema generation settings
    schema_title_override: Optional[str] = Field(None, description="Override schema title")
    schema_description_override: Optional[str] = Field(None, description="Override schema description")
    include_schema_patterns: Optional[List[str]] = Field(None, description="Include only these URL patterns")
    exclude_schema_patterns: Optional[List[str]] = Field(None, description="Exclude these URL patterns")


class SwaggerUISettings(BaseModel):
    """Comprehensive Swagger UI settings for stable documentation."""

    deepLinking: bool = Field(default=True, description="Enable deep linking")
    persistAuthorization: bool = Field(default=True, description="Persist authorization")
    displayOperationId: bool = Field(default=False, description="Display operation ID")
    defaultModelsExpandDepth: int = Field(default=3, description="Default models expand depth")
    defaultModelExpandDepth: int = Field(default=3, description="Default model expand depth")
    defaultModelRendering: str = Field(default="model", description="Default model rendering")
    displayRequestDuration: bool = Field(default=True, description="Display request duration")
    docExpansion: str = Field(default="list", description="Documentation expansion")
    filter: bool = Field(default=True, description="Enable filtering")
    showExtensions: bool = Field(default=True, description="Show extensions")
    showCommonExtensions: bool = Field(default=True, description="Show common extensions")
    tryItOutEnabled: bool = Field(default=True, description="Enable try it out")
    
    # Advanced UI settings for better UX
    supportedSubmitMethods: List[str] = Field(
        default_factory=lambda: ["get", "post", "put", "delete", "patch"],
        description="Supported submit methods"
    )
    validatorUrl: Optional[str] = Field(None, description="Validator URL")
    showMutatedRequest: bool = Field(default=True, description="Show mutated request")


class GeneratorConfig(BaseModel):
    """Comprehensive Python client generator configuration for stable generation."""
    
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    
    # Core settings
    enabled: bool = Field(True, description="Enable Python generation")
    generator_type: str = Field("openapi-python-client", description="Generator to use")
    output_directory: str = Field(
        default_factory=lambda: str(Path.cwd() / "openapi" / "clients" / "python"),
        description="Python output directory",
    )
    
    # Naming templates for consistency
    project_name_template: str = Field("django_revolution_{zone}", description="Project name template")
    package_name_template: str = Field("django_revolution_{zone}", description="Package name template")
    client_class_name_template: str = Field("{zone}Client", description="Client class name template")
    
    # Generation behavior
    overwrite: bool = Field(True, description="Overwrite existing files")
    fail_on_warning: bool = Field(False, description="Fail on warnings")
    auto_format: bool = Field(True, description="Auto-format generated files")
    generate_tests: bool = Field(False, description="Generate test files")
    
    # Modern generator settings for proper enum generation - CRITICAL FOR STABILITY
    use_string_enums: bool = Field(False, description="Use string enums (False = proper Enum classes)")
    generate_aliases: bool = Field(True, description="Generate field aliases")
    use_pydantic_v2: bool = Field(True, description="Use Pydantic v2")
    additional_properties: bool = Field(False, description="Allow additional properties in models")
    datetime_format: str = Field("iso-8601", description="DateTime format")
    
    # HTTP client settings
    http_timeout: int = Field(30, description="HTTP timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retries")
    
    # Code quality settings
    line_length: int = Field(88, description="Line length for formatting")
    use_black: bool = Field(True, description="Use Black for formatting")
    use_isort: bool = Field(True, description="Use isort for import sorting")
    use_mypy: bool = Field(False, description="Generate mypy-compatible code")
    
    # Custom templates and hooks
    custom_templates: Optional[str] = Field(None, description="Path to custom templates")
    post_generation_hooks: List[str] = Field(default_factory=list, description="Post-generation hooks")


class SpectacularConfig(BaseCfgAutoModule):
    """Comprehensive DRF Spectacular configuration for stable schema generation."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.title = "API"
        self.description = "RESTful API"
        self.version = "1.0.0"
        self.schema_path_prefix = "/api/"
        self.contact = None
        self.license_info = None
        self.terms_of_service = None
    
    def get_smart_defaults(self) -> Dict[str, Any]:
        """Get comprehensive defaults optimized for stable enum generation."""
        return {
            # Basic info
            "TITLE": self.title,
            "DESCRIPTION": self.description,
            "VERSION": self.version,
            "SCHEMA_PATH_PREFIX": self.schema_path_prefix,
            
            # Contact and legal info
            "CONTACT": self.contact,
            "LICENSE_INFO": self.license_info,
            "TERMS_OF_SERVICE": self.terms_of_service,
            
            # Schema generation settings - CRITICAL FOR STABILITY
            "SERVE_INCLUDE_SCHEMA": True,
            "COMPONENT_SPLIT_REQUEST": True,
            "COMPONENT_SPLIT_RESPONSE": True,
            "COMPONENT_NO_READ_ONLY_REQUIRED": False,
            
            # Enum generation - MOST IMPORTANT for fixing Optional[str] -> Enum
            "ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE": False,
            "GENERATE_ENUM_FROM_CHOICES": True,
            "ENUM_GENERATE_CHOICE_FROM_PATH": True,
            "ENUM_NAME_SUFFIX": "Enum",
            "CAMELIZE_NAMES": False,
            
            # Advanced enum settings for stability
            "ENUM_NAME_OVERRIDES": {},
            "ENUM_GENERATE_CHOICE_FROM_PATH": True,
            
            # Path and method coercion for stable operation IDs
            "SCHEMA_COERCE_PATH_PK_SUFFIX": True,
            "SCHEMA_COERCE_METHOD_NAMES": {
                "retrieve": "get",
                "destroy": "delete", 
                "partial_update": "patch",
                "update": "put",
                "create": "post",
                "list": "get",
            },
            "SCHEMA_PATH_PREFIX_TRIM": False,
            
            # Generator classes
            "GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
            "SCHEMA_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
            
            # Processing hooks for customization
            "PREPROCESSING_HOOKS": [],
            "POSTPROCESSING_HOOKS": [],
            
            # Error handling
            "DISABLE_ERRORS_AND_WARNINGS": False,
            
            # UI settings with comprehensive configuration
            "SWAGGER_UI_SETTINGS": SwaggerUISettings().model_dump(),
            "SWAGGER_UI_DIST": "SIDECAR",
            "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
            "REDOC_DIST": "SIDECAR",
            
            # Advanced settings for edge cases
            "OPERATION_ID_GENERATOR_CLASS": None,
            "TAGS": None,
            "EXTERNAL_DOCS": None,
            "SERVERS": None,
            
            # Security schemes
            "SECURITY": None,
            "SECURITY_DEFINITIONS": None,
            
            # Extensions and plugins
            "EXTENSIONS_INFO": {},
            "EXTENSIONS": [],
            
            # Sorting and organization
            "SORT_OPERATIONS": True,
            "SORT_OPERATION_PARAMETERS": True,
            
            # Response handling
            "DEFAULT_RESPONSE_CLASS": "rest_framework.response.Response",
            
            # Custom settings for specific use cases
            "CUSTOM_SETTINGS": {},
        }
    
    def get_module_config(self) -> Dict[str, Any]:
        """Get the final Spectacular configuration with all settings."""
        config = self.get_smart_defaults()
        
        # Override with user config if available
        if self._config:
            for attr in ['title', 'description', 'version', 'schema_path_prefix', 
                        'contact', 'license_info', 'terms_of_service']:
                if hasattr(self._config, attr):
                    value = getattr(self._config, attr)
                    if value is not None:
                        config[attr.upper()] = value
        
        return {"SPECTACULAR_SETTINGS": config}


class DRFConfig(BaseCfgAutoModule):
    """Comprehensive DRF configuration for stable API behavior."""
    
    def get_smart_defaults(self) -> Dict[str, Any]:
        """Get comprehensive defaults for DRF with all necessary settings."""
        return {
            # Schema class - CRITICAL for OpenAPI generation
            "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
            
            # Renderers
            "DEFAULT_RENDERER_CLASSES": [
                "rest_framework.renderers.JSONRenderer",
            ],
            
            # Permissions - flexible defaults
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.AllowAny",
            ],
            
            # Authentication - comprehensive support
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
                "rest_framework.authentication.TokenAuthentication",
                "rest_framework.authentication.SessionAuthentication",
            ],
            
            # Parsers - support all common formats
            "DEFAULT_PARSER_CLASSES": [
                "rest_framework.parsers.JSONParser",
                "rest_framework.parsers.FormParser",
                "rest_framework.parsers.MultiPartParser",
            ],
            
            # Pagination - stable defaults
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 20,
            
            # Filtering - comprehensive support
            "DEFAULT_FILTER_BACKENDS": [
                "django_filters.rest_framework.DjangoFilterBackend",
                "rest_framework.filters.SearchFilter",
                "rest_framework.filters.OrderingFilter",
            ],
            
            # Versioning
            "DEFAULT_VERSIONING_CLASS": None,
            "DEFAULT_VERSION": None,
            "ALLOWED_VERSIONS": None,
            "VERSION_PARAM": "version",
            
            # Content negotiation
            "DEFAULT_CONTENT_NEGOTIATION_CLASS": "rest_framework.negotiation.DefaultContentNegotiation",
            
            # Metadata
            "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
            
            # Throttling - disabled by default but configurable
            "DEFAULT_THROTTLE_CLASSES": [],
            "DEFAULT_THROTTLE_RATES": {
                "anon": "100/hour",
                "user": "1000/hour",
            },
            
            # Exception handling
            "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
            
            # Testing
            "TEST_REQUEST_DEFAULT_FORMAT": "json",
            "TEST_REQUEST_RENDERER_CLASSES": [
                "rest_framework.renderers.MultiPartRenderer",
                "rest_framework.renderers.JSONRenderer",
            ],
            
            # URL format
            "URL_FORMAT_OVERRIDE": "format",
            "FORMAT_SUFFIX_KWARG": "format",
            
            # Unicode handling
            "UNICODE_JSON": True,
            "COMPACT_JSON": True,
            
            # Charset
            "CHARSET": "utf-8",
            
            # JSON settings
            "DEFAULT_JSON_INDENT": 2,
            "STRICT_JSON": True,
            
            # CORS and security
            "ALLOWED_HOSTS": ["*"],
            
            # Custom settings placeholder
            "CUSTOM_SETTINGS": {},
        }
    
    def get_module_config(self) -> Dict[str, Any]:
        """Get the final DRF configuration with all settings."""
        config = self.get_smart_defaults()
        
        # Add custom settings if available
        if self._config and hasattr(self._config, 'custom_rest_framework_settings'):
            config.update(self._config.custom_rest_framework_settings)
        
        return {"REST_FRAMEWORK": config}


class RevolutionConfig(BaseSettings):
    """Main Django Revolution configuration with comprehensive settings."""
    
    model_config = SettingsConfigDict(
        env_prefix="DJANGO_REVOLUTION_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )
    
    # Core settings
    api_prefix: str = Field("api", description="API prefix for all routes")
    debug: bool = Field(False, description="Enable debug mode")
    auto_install_deps: bool = Field(True, description="Auto-install dependencies")
    version: str = Field("1.0.35", description="Package version")
    
    # Multithreading settings for performance
    max_workers: int = Field(20, description="Maximum worker threads for generation")
    enable_multithreading: bool = Field(True, description="Enable multithreaded generation")
    
    # Output settings
    base_output_directory: str = Field(
        default_factory=lambda: str(Path.cwd() / "openapi"),
        description="Base output directory"
    )
    
    # Generator settings
    python: GeneratorConfig = Field(default_factory=GeneratorConfig)
    
    # Zone configuration
    zones: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Archive settings
    enable_archiving: bool = Field(True, description="Enable client archiving")
    archive_format: str = Field("zip", description="Archive format")
    keep_archive_history: bool = Field(True, description="Keep archive history")
    max_archive_files: int = Field(10, description="Maximum archive files to keep")
    
    @classmethod
    def from_django_settings(cls) -> "RevolutionConfig":
        """Create settings from Django settings if available."""
        kwargs = {}
        
        if django_settings and hasattr(django_settings, "DJANGO_REVOLUTION"):
            django_config = django_settings.DJANGO_REVOLUTION
            kwargs.update(django_config)
        
        return cls(**kwargs)
    
    def get_zones(self) -> Dict[str, ZoneConfig]:
        """Get validated zone models."""
        zones = {}
        for zone_name, zone_config in self.zones.items():
            zones[zone_name] = ZoneConfig(**zone_config)
        return zones
    
    @field_validator("zones")
    @classmethod
    def validate_zones(cls, v):
        """Validate zone configurations for stability."""
        if not v:
            return v
        
        validated_zones = {}
        all_apps = set()
        all_prefixes = set()
        
        for zone_name, zone_config in v.items():
            # Validate zone structure
            if not isinstance(zone_config, dict):
                raise ValueError(f"Zone '{zone_name}' must be a dictionary")
            
            # Check required fields
            required_fields = ['apps', 'title', 'description']
            for field in required_fields:
                if field not in zone_config:
                    raise ValueError(f"Zone '{zone_name}' missing required field: {field}")
            
            # Check for duplicate apps across zones
            zone_apps = set(zone_config.get('apps', []))
            duplicate_apps = zone_apps & all_apps
            if duplicate_apps:
                raise ValueError(f"Duplicate apps across zones: {duplicate_apps}")
            all_apps.update(zone_apps)
            
            # Check for duplicate prefixes
            prefix = zone_config.get('path_prefix', zone_name)
            if prefix in all_prefixes:
                raise ValueError(f"Duplicate path prefix '{prefix}' in zone '{zone_name}'")
            all_prefixes.add(prefix)
            
            validated_zones[zone_name] = zone_config
        
        return validated_zones


# Convenience functions for easy setup with comprehensive configuration
def create_drf_spectacular_config(
    title: str = "API",
    description: str = "RESTful API", 
    version: str = "1.0.0",
    schema_path_prefix: str = "/api/",
    contact: Optional[Dict[str, str]] = None,
    license_info: Optional[Dict[str, str]] = None,
    enable_browsable_api: bool = False,
    enable_throttling: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Create complete DRF + Spectacular configuration with comprehensive settings.
    
    This is the main function users should use for setup with all stability features.
    """
    # Create config objects with full settings
    spectacular = SpectacularConfig()
    spectacular.title = title
    spectacular.description = description
    spectacular.version = version
    spectacular.schema_path_prefix = schema_path_prefix
    spectacular.contact = contact
    spectacular.license_info = license_info
    
    drf = DRFConfig()
    
    # Get base configurations
    settings = {}
    settings.update(drf.get_module_config())
    settings.update(spectacular.get_module_config())
    
    # Add browsable API if requested
    if enable_browsable_api:
        settings["REST_FRAMEWORK"]["DEFAULT_RENDERER_CLASSES"].append(
            "rest_framework.renderers.BrowsableAPIRenderer"
        )
    
    # Add throttling if requested
    if enable_throttling:
        settings["REST_FRAMEWORK"]["DEFAULT_THROTTLE_CLASSES"] = [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ]
    
    # Apply any custom overrides
    for key, value in kwargs.items():
        if key.startswith("SPECTACULAR_"):
            settings["SPECTACULAR_SETTINGS"][key] = value
        elif key.startswith("REST_FRAMEWORK_"):
            settings["REST_FRAMEWORK"][key.replace("REST_FRAMEWORK_", "")] = value
    
    return settings


def create_revolution_zones(zones_dict: Dict[str, Dict[str, Any]]) -> Dict[str, ZoneConfig]:
    """Create zone configurations from dictionary with validation."""
    zones = {}
    for zone_name, zone_data in zones_dict.items():
        zones[zone_name] = ZoneConfig(**zone_data)
    return zones


# Global settings instance
_settings_instance = None


def get_settings() -> RevolutionConfig:
    """Get global settings instance with comprehensive configuration."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = RevolutionConfig.from_django_settings()
    return _settings_instance


# Export main classes and functions
__all__ = [
    "BaseCfgAutoModule",
    "ZoneConfig", 
    "GeneratorConfig",
    "SpectacularConfig",
    "DRFConfig",
    "RevolutionConfig",
    "SwaggerUISettings",
    "create_drf_spectacular_config",
    "create_revolution_zones",
    "get_settings",
]