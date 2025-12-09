"""
Base settings for extension modules.

Extension modules are utility libraries without Django models
that can be optionally enabled per project.
"""

from typing import TYPE_CHECKING, List, Literal, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from django_cfg.extensions.manifest import ExtensionManifest


class BaseModuleSettings(BaseModel):
    """Base settings for all extension modules."""

    # Module identification
    name: str = Field(..., description="Module name (e.g., 'currency')")
    version: str = Field(default="1.0.0", description="Module version")
    description: str = Field(default="", description="Module description")

    # Module type identifier
    type: Literal["module"] = "module"

    # Dependencies
    requires: List[str] = Field(
        default_factory=list,
        description="Other django_cfg modules this module depends on"
    )
    pip_requires: List[str] = Field(
        default_factory=list,
        description="Python packages required by this module"
    )

    # Feature flags
    enabled: bool = Field(
        default=True,
        description="Whether this module is enabled"
    )

    model_config = {
        "extra": "forbid",
        "frozen": False,
    }

    def to_manifest(self) -> "ExtensionManifest":
        """
        Convert settings to ExtensionManifest for scanner compatibility.

        Returns:
            ExtensionManifest instance
        """
        from django_cfg.extensions.manifest import ExtensionManifest

        return ExtensionManifest(
            name=self.name,
            version=self.version,
            description=self.description,
            type="module",
            requires=self.requires,
            pip_requires=self.pip_requires,
            admin_enabled=False,
            has_migrations=False,
        )

    def check_dependencies(self) -> List[str]:
        """
        Check if all pip dependencies are installed.

        Returns:
            List of missing packages
        """
        missing = []
        for package in self.pip_requires:
            # Extract package name without version specifier
            pkg_name = package.split(">=")[0].split("==")[0].split("<")[0].strip()
            try:
                __import__(pkg_name.replace("-", "_"))
            except ImportError:
                missing.append(package)
        return missing
