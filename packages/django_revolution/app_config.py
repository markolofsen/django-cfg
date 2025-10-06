"""
Django Revolution Configuration Models
Zone-based API client generator settings
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ZoneConfig(BaseModel):
    """Zone configuration for API generation."""

    model_config = ConfigDict(extra="forbid")

    apps: List[str] = Field(..., description="List of Django apps in this zone")
    title: str = Field(..., description="Zone title")
    description: str = Field(..., description="Zone description")
    public: bool = Field(True, description="Is zone public")
    auth_required: bool = Field(False, description="Authentication required")
    version: str = Field("v1", description="API version")


class DjangoRevolutionConfig(BaseModel):
    """Django Revolution main configuration."""

    model_config = ConfigDict(extra="forbid")

    api_prefix: str = Field("apix", description="API prefix for all routes")
    debug: bool = Field(False, description="Enable debug mode")
    auto_install_deps: bool = Field(True, description="Auto-install dependencies")
    zones: Dict[str, ZoneConfig] = Field(..., description="Zone configurations")

    def to_django_config(self) -> Dict[str, Any]:
        """Convert to Django settings format with proper serialization."""
        return self.model_dump(mode="json", exclude_none=True)


def get_revolution_config(
    project_root: Path,
    zones: Dict[str, ZoneConfig],
    debug: bool = False,
    api_prefix: str = "apix",
) -> Dict[str, Any]:
    """Get Django Revolution configuration as dictionary."""

    config = DjangoRevolutionConfig(
        api_prefix=api_prefix,
        debug=debug,
        auto_install_deps=True,
        zones=zones,
    )

    return config.model_dump()


def setup_revolution(
    project_root: Path,
    zones: Dict[str, ZoneConfig],
    debug: bool = False,
    api_prefix: str = "apix",
) -> Dict[str, Any]:
    """Alias for get_revolution_config for backward compatibility."""
    return get_revolution_config(
        project_root=project_root, zones=zones, debug=debug, api_prefix=api_prefix
    )
