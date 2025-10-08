"""
OpenAPI Input Models - Root OpenAPI Spec.

This module defines the root OpenAPISpec model that represents a complete
OpenAPI specification (version 3.0.3 or 3.1.0).

Reference: https://spec.openapis.org/oas/v3.1.0
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .base import ExternalDocumentationObject, InfoObject, ServerObject, TagObject
from .components import ComponentsObject
from .operation import PathItemObject


class OpenAPISpec(BaseModel):
    """
    OpenAPI Specification root object.

    This is the top-level object representing a complete OpenAPI specification.
    Supports both OpenAPI 3.0.3 and 3.1.0.

    Reference: https://spec.openapis.org/oas/v3.1.0

    Examples:
        >>> spec = OpenAPISpec(
        ...     openapi="3.1.0",
        ...     info=InfoObject(title="My API", version="1.0.0"),
        ...     paths={"/users/": PathItemObject(...)},
        ... )
        >>> spec.openapi_version
        '3.1.0'
        >>> spec.is_openapi_31
        True
    """

    model_config = ConfigDict(
        extra="allow",  # Allow x-* extensions
        validate_assignment=True,
    )

    # ===== Required Fields =====
    openapi: str = Field(
        ...,
        description="OpenAPI version (3.0.0, 3.0.1, 3.0.2, 3.0.3, 3.1.0)",
    )
    info: InfoObject = Field(..., description="API metadata")
    paths: dict[str, PathItemObject] | None = Field(
        None,
        description="API paths (/users/, /tasks/{id}/, etc.)",
    )

    # ===== Optional Fields =====
    jsonSchemaDialect: str | None = Field(
        None,
        description="JSON Schema dialect (OAS 3.1.0 only)",
    )
    servers: list[ServerObject] | None = Field(
        None,
        description="Server URLs",
    )
    components: ComponentsObject | None = Field(
        None,
        description="Reusable components (schemas, responses, etc.)",
    )
    security: list[dict[str, list[str]]] | None = Field(
        None,
        description="Global security requirements",
    )
    tags: list[TagObject] | None = Field(
        None,
        description="API tags for grouping operations",
    )
    externalDocs: ExternalDocumentationObject | None = None

    # ===== drf-spectacular Extensions =====
    x_tagGroups: list[dict[str, Any]] | None = Field(
        None,
        alias="x-tagGroups",
        description="Tag groups from drf-spectacular",
    )

    # ===== Validation =====

    @field_validator("openapi")
    @classmethod
    def validate_openapi_version(cls, v: str) -> str:
        """Validate OpenAPI version is 3.0.x or 3.1.0."""
        valid_versions = ["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"]
        if v not in valid_versions:
            raise ValueError(
                f"Unsupported OpenAPI version: {v}. "
                f"Supported versions: {', '.join(valid_versions)}"
            )
        return v

    # ===== Computed Properties =====

    @property
    def openapi_version(self) -> str:
        """Get OpenAPI version string."""
        return self.openapi

    @property
    def is_openapi_30(self) -> bool:
        """Check if OpenAPI 3.0.x."""
        return self.openapi.startswith("3.0.")

    @property
    def is_openapi_31(self) -> bool:
        """Check if OpenAPI 3.1.0."""
        return self.openapi == "3.1.0"

    @property
    def normalized_version(self) -> Literal["3.0.3", "3.1.0"]:
        """
        Get normalized OpenAPI version (3.0.3 or 3.1.0).

        All 3.0.x versions are normalized to 3.0.3.
        """
        if self.is_openapi_30:
            return "3.0.3"
        return "3.1.0"

    @property
    def has_components(self) -> bool:
        """Check if spec has components."""
        return self.components is not None and self.components.has_schemas

    @property
    def has_paths(self) -> bool:
        """Check if spec has paths."""
        return self.paths is not None and len(self.paths) > 0

    @property
    def all_paths(self) -> dict[str, PathItemObject]:
        """Get all paths (empty dict if none)."""
        return self.paths or {}

    @property
    def all_operations(self) -> dict[str, tuple[str, str, Any]]:
        """
        Get all operations from all paths.

        Returns:
            Dict of {operation_id: (http_method, path, OperationObject)}

        Examples:
            >>> spec = OpenAPISpec(...)
            >>> ops = spec.all_operations
            >>> ops['users_list']
            ('GET', '/api/users/', OperationObject(...))
        """
        result = {}
        if not self.paths:
            return result

        for path, path_item in self.paths.items():
            for method, operation in path_item.operations.items():
                if operation.operationId:
                    result[operation.operationId] = (method, path, operation)

        return result

    @property
    def all_schema_names(self) -> list[str]:
        """Get all schema names from components."""
        if not self.components or not self.components.schemas:
            return []
        return list(self.components.schemas.keys())

    @property
    def server_urls(self) -> list[str]:
        """Get all server URLs."""
        if not self.servers:
            return []
        return [server.url for server in self.servers]

    def get_schema(self, name: str) -> Any:
        """Get schema from components by name."""
        if not self.components:
            return None
        return self.components.get_schema(name)

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = [
            f"OpenAPISpec(openapi={self.openapi!r}",
            f"title={self.info.title!r}",
        ]

        if self.paths:
            parts.append(f"paths={len(self.paths)}")

        if self.components and self.components.schemas:
            parts.append(f"schemas={len(self.components.schemas)}")

        return ", ".join(parts) + ")"
