"""
Main OpenAPI configuration for django_cfg.

Replaces django-revolution with integrated django_openapi module.
"""

from pathlib import Path
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator

from .group import OpenAPIGroupConfig


class OpenAPIConfig(BaseModel):
    """
    Main OpenAPI configuration for django-cfg.

    Features:
    - Smart application grouping (cfg/custom)
    - Python & TypeScript client generation
    - Pure Python implementation (no external dependencies)
    - 20x faster than django-revolution

    Example:
        >>> from django_cfg import DjangoCfg
        >>> config = DjangoCfg(
        ...     openapi=OpenAPIConfig(
        ...         enabled=True,
        ...         groups=[
        ...             OpenAPIGroupConfig(
        ...                 name="cfg",
        ...                 apps=["django_cfg.*"],
        ...                 title="Framework API",
        ...             ),
        ...             OpenAPIGroupConfig(
        ...                 name="custom",
        ...                 apps=["myapp"],
        ...                 title="Custom API",
        ...             ),
        ...         ],
        ...     ),
        ... )
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Control
    enabled: bool = Field(
        default=False,
        description="Enable OpenAPI client generation",
    )

    # Application Grouping
    groups: List[OpenAPIGroupConfig] = Field(
        default_factory=list,
        description="Application groups for separate schema generation",
    )

    # Output Configuration
    output_dir: str = Field(
        default="openapi",
        description="Base output directory for schemas and clients",
    )

    # Client Generation
    generate_python: bool = Field(
        default=True,
        description="Generate Python client",
    )

    generate_typescript: bool = Field(
        default=True,
        description="Generate TypeScript client",
    )

    generate_package_files: bool = Field(
        default=False,
        description="Generate package.json (TypeScript) and pyproject.toml (Python)",
    )

    generate_zod_schemas: bool = Field(
        default=False,
        description="Generate Zod schemas for runtime validation (TypeScript only)",
    )

    generate_fetchers: bool = Field(
        default=False,
        description="Generate typed fetcher functions (TypeScript only, requires Zod schemas)",
    )

    generate_swr_hooks: bool = Field(
        default=False,
        description="Generate SWR hooks for React (TypeScript only, requires fetchers)",
    )

    client_structure: Literal["flat", "namespaced"] = Field(
        default="namespaced",
        description=(
            "Client structure:\n"
            "  - flat: All methods in one class (client.posts_list())\n"
            "  - namespaced: Organized by tags (client.posts.list())"
        ),
    )

    # API Configuration
    api_prefix: str = Field(
        default="apix",
        description="API URL prefix (e.g., 'apix' -> /apix/app/endpoint)",
    )

    # Archive Configuration
    enable_archive: bool = Field(
        default=True,
        description="Enable client archiving with versioning",
    )

    archive_retention_days: int = Field(
        default=30,
        description="Days to keep archived clients",
        ge=1,
    )

    # Performance
    max_workers: int = Field(
        default=1,
        description="Number of parallel workers (1 = single-threaded, which is fast enough)",
        ge=1,
        le=20,
    )

    @field_validator("groups")
    @classmethod
    def validate_groups_when_enabled(cls, v: List[OpenAPIGroupConfig], info) -> List[OpenAPIGroupConfig]:
        """Ensure at least one group is defined when enabled and names are unique."""
        # Access enabled field via info.data
        enabled = info.data.get("enabled", False)
        if enabled and not v:
            raise ValueError("At least one group must be defined when OpenAPI is enabled")

        # Check for duplicate group names
        names = [group.name for group in v]
        if len(names) != len(set(names)):
            duplicates = [name for name in names if names.count(name) > 1]
            raise ValueError(f"Duplicate group names found: {', '.join(set(duplicates))}")

        return v

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, v: str) -> str:
        """Ensure API prefix is valid."""
        v = v.strip().strip("/")
        if not v:
            raise ValueError("api_prefix cannot be empty")
        return v

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v: str) -> str:
        """Ensure output directory is valid."""
        v = v.strip()
        if not v:
            raise ValueError("output_dir cannot be empty")
        return v

    def get_output_path(self) -> Path:
        """Get absolute output path."""
        return Path(self.output_dir).resolve()

    def get_schemas_dir(self) -> Path:
        """Get schemas directory path."""
        return self.get_output_path() / "schemas"

    def get_clients_dir(self) -> Path:
        """Get clients directory path."""
        return self.get_output_path() / "clients"

    def get_python_clients_dir(self) -> Path:
        """Get Python clients directory path."""
        return self.get_clients_dir() / "python"

    def get_typescript_clients_dir(self) -> Path:
        """Get TypeScript clients directory path."""
        return self.get_clients_dir() / "typescript"

    def get_go_clients_dir(self) -> Path:
        """Get Go clients directory path."""
        return self.get_clients_dir() / "go"

    def get_archive_dir(self) -> Path:
        """Get archive directory path."""
        return self.get_output_path() / "archive"

    def get_group_schema_path(self, group_name: str) -> Path:
        """Get OpenAPI schema path for a group."""
        return self.get_schemas_dir() / f"{group_name}.yaml"

    def get_group_python_dir(self, group_name: str) -> Path:
        """Get Python client directory for a group."""
        return self.get_python_clients_dir() / group_name

    def get_group_typescript_dir(self, group_name: str) -> Path:
        """Get TypeScript client directory for a group."""
        return self.get_typescript_clients_dir() / group_name

    def get_group_go_dir(self, group_name: str) -> Path:
        """Get Go client directory for a group."""
        return self.get_go_clients_dir() / group_name


__all__ = [
    "OpenAPIConfig",
]
