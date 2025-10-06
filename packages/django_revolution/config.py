"""
Django Revolution Configuration

Comprehensive configuration management using Pydantic for validation.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from django.conf import settings
except ImportError:
    settings = None


class ZoneModel(BaseModel):
    """Pydantic model for API zone configuration."""

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, str_strip_whitespace=True, frozen=True
    )

    name: str = Field(..., min_length=1, description="Zone name")
    apps: List[str] = Field(
        ..., min_items=1, description="List of Django apps in this zone"
    )
    title: Optional[str] = Field(None, description="Human-readable title")
    description: Optional[str] = Field(None, description="Zone description")
    public: bool = Field(True, description="Whether zone is publicly accessible")
    auth_required: bool = Field(False, description="Whether authentication is required")
    rate_limit: Optional[str] = Field(None, description="Rate limit configuration")
    permissions: Optional[List[str]] = Field(None, description="Required permissions")
    version: str = Field("1.0.43", description="API version")
    prefix: Optional[str] = Field(None, description="URL prefix override")
    cors_enabled: bool = Field(False, description="Enable CORS for this zone")
    middleware: Optional[List[str]] = Field(None, description="Custom middleware")
    path_prefix: Optional[str] = Field(None, description="Path prefix for URLs")

    @field_validator("apps")
    @classmethod
    def validate_apps(cls, v):
        if not v:
            raise ValueError("Apps list cannot be empty")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Zone name cannot be empty")
        return v.strip().lower()

    def __post_init_post_parse__(self):
        # Set defaults based on name
        if not self.title:
            self.title = self.name.replace("_", " ").title()
        if not self.path_prefix:
            self.path_prefix = self.name


class OutputSettings(BaseModel):
    """Output directory configuration."""

    model_config = ConfigDict(validate_assignment=True)

    base_directory: str = Field(
        default_factory=lambda: str(Path.cwd() / "openapi"),
        description="Base output directory",
    )
    schemas_directory: str = Field(
        "schemas", description="Directory for OpenAPI schemas"
    )
    clients_directory: str = Field(
        "clients", description="Directory for generated clients"
    )
    temp_directory: str = Field(
        "openapi/temp", description="Temporary directory"
    )
    archive_directory_ts: str = Field(
        "archive/typescript", description="TypeScript archive directory"
    )
    archive_directory_py: str = Field(
        "archive/python", description="Python archive directory"
    )

    @field_validator("base_directory")
    @classmethod
    def validate_base_directory(cls, v):
        path = Path(v)
        if not path.is_absolute():
            path = Path.cwd() / path
        return str(path)

    @field_validator("temp_directory")
    @classmethod
    def validate_temp_directory(cls, v):
        path = Path(v)
        if not path.is_absolute():
            path = Path.cwd() / path
        return str(path)


class TypeScriptGeneratorSettings(BaseModel):
    """TypeScript generator configuration."""

    model_config = ConfigDict(validate_assignment=True)

    enabled: bool = Field(True, description="Enable TypeScript generation")
    output_directory: str = Field(
        default_factory=lambda: str(Path.cwd() / "openapi" / "clients" / "typescript"),
        description="TypeScript output directory",
    )
    output_format: str = Field("prettier", description="Output format (prettier, none)")
    generate_tests: bool = Field(False, description="Generate test files")
    custom_templates: Optional[str] = Field(
        None, description="Path to custom templates"
    )
    auto_format: bool = Field(True, description="Automatically format generated files with Prettier")

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v):
        path = Path(v)
        if not path.is_absolute():
            path = Path.cwd() / path
        return str(path)


class PythonGeneratorSettings(BaseModel):
    """Python generator configuration."""

    model_config = ConfigDict(validate_assignment=True)

    enabled: bool = Field(True, description="Enable Python generation")
    output_directory: str = Field(
        default_factory=lambda: str(Path.cwd() / "openapi" / "clients" / "python"),
        description="Python output directory",
    )
    project_name_template: str = Field(
        "django_revolution_{zone}", description="Project name template"
    )
    package_name_template: str = Field(
        "django_revolution_{zone}", description="Package name template"
    )
    overwrite: bool = Field(True, description="Overwrite existing files")
    fail_on_warning: bool = Field(False, description="Fail on warnings")
    custom_templates: Optional[str] = Field(
        None, description="Path to custom templates"
    )
    auto_format: bool = Field(True, description="Automatically format generated files with Black")

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v):
        path = Path(v)
        if not path.is_absolute():
            path = Path.cwd() / path
        return str(path)


class GeneratorsSettings(BaseModel):
    """Generators configuration."""

    model_config = ConfigDict(validate_assignment=True)

    typescript: TypeScriptGeneratorSettings = Field(
        default_factory=TypeScriptGeneratorSettings
    )
    python: PythonGeneratorSettings = Field(default_factory=PythonGeneratorSettings)





class GenerationResult(BaseModel):
    """Result of a generation process."""

    model_config = ConfigDict(validate_assignment=True)

    success: bool = Field(..., description="Whether generation was successful")
    zone_name: str = Field(..., description="Zone name")
    output_path: Path = Field(..., description="Output path")
    files_generated: int = Field(0, description="Number of files generated")
    error_message: str = Field("", description="Error message if failed")


class GenerationSummary(BaseModel):
    """Summary of generation process."""

    model_config = ConfigDict(validate_assignment=True)

    total_zones: int = Field(..., description="Total number of zones")
    successful_typescript: int = Field(
        0, description="Successful TypeScript generations"
    )
    successful_python: int = Field(0, description="Successful Python generations")
    failed_typescript: int = Field(0, description="Failed TypeScript generations")
    failed_python: int = Field(0, description="Failed Python generations")
    total_files_generated: int = Field(0, description="Total files generated")
    duration_seconds: float = Field(0.0, description="Total duration in seconds")
    typescript_results: Dict[str, GenerationResult] = Field(default_factory=dict)
    python_results: Dict[str, GenerationResult] = Field(default_factory=dict)


class DjangoRevolutionSettings(BaseSettings):
    """Main Django Revolution settings using Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_prefix="DJANGO_REVOLUTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_assignment=True,
    )

    # Core settings
    api_prefix: str = Field("apix", description="API prefix for all routes")
    debug: bool = Field(False, description="Enable debug mode")
    auto_install_deps: bool = Field(True, description="Auto-install dependencies")
    version: str = Field("1.0.43", description="Package version for generated clients")

    # Multithreading settings
    max_workers: int = Field(
        20, description="Maximum number of worker threads for schema generation"
    )
    enable_multithreading: bool = Field(
        True, description="Enable multithreaded schema generation"
    )

    # Output configuration
    output: OutputSettings = Field(default_factory=OutputSettings)

    # Generators configuration
    generators: GeneratorsSettings = Field(default_factory=GeneratorsSettings)

    # Zone configuration
    zones: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Zone configurations"
    )

    @classmethod
    def from_django_settings(cls) -> "DjangoRevolutionSettings":
        """Create settings from Django settings if available."""
        kwargs = {}

        if settings and hasattr(settings, "DJANGO_REVOLUTION"):
            django_config = settings.DJANGO_REVOLUTION
            kwargs.update(django_config)

        return cls(**kwargs)

    @field_validator("zones")
    @classmethod
    def validate_zones(cls, v):
        """Validate zone configurations."""
        if not v:
            return v

        validated_zones = {}
        all_apps = set()
        all_prefixes = set()

        for zone_name, zone_config in v.items():
            # Create ZoneModel to validate
            zone_model = ZoneModel(name=zone_name, **zone_config)

            # Check for duplicate apps across zones
            zone_apps = set(zone_model.apps)
            duplicate_apps = zone_apps & all_apps
            if duplicate_apps:
                raise ValueError(f"Duplicate apps across zones: {duplicate_apps}")
            all_apps.update(zone_apps)

            # Check for duplicate prefixes
            prefix = zone_model.path_prefix or zone_name
            if prefix in all_prefixes:
                raise ValueError(
                    f"Duplicate path prefix '{prefix}' in zone '{zone_name}'"
                )
            all_prefixes.add(prefix)

            validated_zones[zone_name] = zone_config

        return validated_zones

    def get_zones(self) -> Dict[str, ZoneModel]:
        """Get validated zone models."""
        zones = {}
        for zone_name, zone_config in self.zones.items():
            zones[zone_name] = ZoneModel(name=zone_name, **zone_config)
        return zones

    def get_zone(self, name: str) -> Optional[ZoneModel]:
        """Get a specific zone by name."""
        if name in self.zones:
            return ZoneModel(name=name, **self.zones[name])
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            "api_prefix": self.api_prefix,
            "debug": self.debug,
            "auto_install_deps": self.auto_install_deps,
            "version": self.version,
            "max_workers": self.max_workers,
            "enable_multithreading": self.enable_multithreading,
            "output": self.output.model_dump(),
            "generators": self.generators.model_dump(),
            "zones": self.zones,
        }


# Global settings instance
_settings_instance = None


def get_settings() -> DjangoRevolutionSettings:
    """Get global settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = DjangoRevolutionSettings.from_django_settings()
    return _settings_instance


def get_config() -> Dict[str, Any]:
    """Get configuration as dictionary."""
    return get_settings().to_dict()
