"""
OpenAPI Group Configuration.

Defines application grouping (cfg/custom) for separate schema generation.
"""

from typing import List

from pydantic import BaseModel, Field, field_validator


class OpenAPIGroupConfig(BaseModel):
    """
    Configuration for a single application group.

    Groups organize Django apps into separate OpenAPI schemas and clients.

    Example:
        >>> cfg_group = OpenAPIGroupConfig(
        ...     name="cfg",
        ...     apps=["django_cfg.*"],
        ...     title="Django Config Framework API",
        ...     description="Core framework functionality",
        ... )
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }

    # Group identification
    name: str = Field(
        ...,
        description="Unique name for this group (used for file paths and identification)",
        min_length=1,
    )

    # App selection
    apps: List[str] = Field(
        ...,
        description="List of Django apps in this group. Supports wildcards (e.g., 'django_cfg.*')",
        min_length=1,
    )

    # Metadata
    title: str = Field(
        ...,
        description="Human-readable title for this group",
        min_length=1,
    )

    description: str = Field(
        default="",
        description="Detailed description for this group",
    )

    # API configuration
    version: str = Field(
        default="v1",
        description="API version string",
    )

    # Authentication
    auth_required: bool = Field(
        default=False,
        description="Whether authentication is required for this group",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is valid (alphanumeric + underscore/hyphen)."""
        import re
        v = v.strip()
        if not v:
            raise ValueError("name cannot be empty")
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("name must contain only alphanumeric characters, underscores, or hyphens")
        return v

    @field_validator("apps")
    @classmethod
    def validate_apps_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure apps list is not empty."""
        if not v:
            raise ValueError("apps list cannot be empty")
        return v

    @field_validator("title")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not empty."""
        if not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip()


__all__ = [
    "OpenAPIGroupConfig",
]
