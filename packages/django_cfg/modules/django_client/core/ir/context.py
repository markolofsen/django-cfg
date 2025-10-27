"""
IR Context - Root model for unified API representation.

This module defines the root IRContext model that contains:
- All schemas (User, UserRequest, PatchedUser, etc.)
- All operations (endpoints)
- Django global metadata (COMPONENT_SPLIT_REQUEST, auth, etc.)
- OpenAPI metadata (version, title, servers)

Key Features:
- Single source of truth for code generation
- Version-agnostic (normalized from 3.0.3 and 3.1.0)
- Django-aware (validates COMPONENT_SPLIT_REQUEST)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .operation import IROperationObject
from .schema import IRSchemaObject


class OpenAPIInfo(BaseModel):
    """
    OpenAPI specification metadata.

    Examples:
        >>> info = OpenAPIInfo(
        ...     version="3.1.0",
        ...     title="My Django API",
        ...     description="RESTful API for my Django app",
        ...     api_version="1.0.0",
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    version: Literal["3.0.3", "3.1.0"] = Field(
        ..., description="OpenAPI version (3.0.3 or 3.1.0)"
    )
    title: str = Field(..., description="API title")
    description: str | None = Field(None, description="API description")
    api_version: str = Field("1.0.0", description="API version (e.g., '1.0.0')")

    # Servers
    servers: list[str] = Field(
        default_factory=list,
        description="Server URLs (e.g., ['https://api.example.com', 'http://localhost:8000'])",
    )

    # Contact and license
    contact_name: str | None = Field(None, description="Contact name")
    contact_email: str | None = Field(None, description="Contact email")
    license_name: str | None = Field(None, description="License name (e.g., 'MIT')")
    license_url: str | None = Field(None, description="License URL")

    @property
    def is_openapi_31(self) -> bool:
        """Check if OpenAPI 3.1.0."""
        return self.version == "3.1.0"

    @property
    def is_openapi_30(self) -> bool:
        """Check if OpenAPI 3.0.3."""
        return self.version == "3.0.3"

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"OpenAPIInfo(version={self.version!r}, title={self.title!r}, api_version={self.api_version!r})"


class DjangoGlobalMetadata(BaseModel):
    """
    Django global metadata from drf-spectacular settings.

    This model captures critical Django/DRF configuration that affects
    code generation. Most importantly, it validates that COMPONENT_SPLIT_REQUEST
    is enabled (mandatory for correct Request/Response split).

    Examples:
        >>> # Correct configuration
        >>> metadata = DjangoGlobalMetadata(
        ...     component_split_request=True,
        ...     component_split_patch=True,
        ...     oas_version="3.1.0",
        ... )

        >>> # Missing COMPONENT_SPLIT_REQUEST (will raise validation error)
        >>> bad_metadata = DjangoGlobalMetadata(
        ...     component_split_request=False,  # ❌ FORBIDDEN!
        ... )
        Traceback (most recent call last):
        ...
        ValueError: COMPONENT_SPLIT_REQUEST must be True
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    # ===== CRITICAL: drf-spectacular Settings =====
    component_split_request: bool = Field(
        ...,
        description="COMPONENT_SPLIT_REQUEST setting (MUST be True for correct code generation)",
    )
    component_split_patch: bool = Field(
        True,
        description="COMPONENT_SPLIT_PATCH setting (separate PatchedUser models)",
    )
    oas_version: Literal["3.0.3", "3.1.0"] = Field(
        "3.1.0",
        description="OAS_VERSION setting (3.1.0 recommended)",
    )

    # ===== Default Authentication/Permissions =====
    default_authentication_classes: list[str] = Field(
        default_factory=list,
        description="Default authentication classes (e.g., ['SessionAuthentication'])",
    )
    default_permission_classes: list[str] = Field(
        default_factory=list,
        description="Default permission classes (e.g., ['IsAuthenticated'])",
    )

    # ===== CSRF =====
    csrf_cookie_name: str = Field(
        "csrftoken",
        description="Django CSRF cookie name (default: 'csrftoken')",
    )
    csrf_header_name: str = Field(
        "X-CSRFToken",
        description="Django CSRF header name (default: 'X-CSRFToken')",
    )

    # ===== Session =====
    session_cookie_name: str = Field(
        "sessionid",
        description="Django session cookie name (default: 'sessionid')",
    )

    # ===== Computed Properties =====

    @property
    def has_session_auth(self) -> bool:
        """
        Check if SessionAuthentication is enabled in DRF defaults.

        Returns True if any authentication class contains 'SessionAuthentication'.
        """
        return any(
            'SessionAuthentication' in auth_class
            for auth_class in self.default_authentication_classes
        )

    # ===== Validation =====

    @field_validator("component_split_request")
    @classmethod
    def validate_component_split_request(cls, v: bool) -> bool:
        """
        Validate that COMPONENT_SPLIT_REQUEST is True.

        This is MANDATORY for correct Request/Response split.
        Without it, generators will create broken models.

        Raises:
            ValueError: If COMPONENT_SPLIT_REQUEST is False.
        """
        if not v:
            raise ValueError(
                "COMPONENT_SPLIT_REQUEST must be True! "
                "This is mandatory for correct Request/Response model generation. "
                "Add this to your Django settings:\n\n"
                "SPECTACULAR_SETTINGS = {\n"
                "    'COMPONENT_SPLIT_REQUEST': True,\n"
                "    'COMPONENT_SPLIT_PATCH': True,\n"
                "}\n\n"
                "See: https://drf-spectacular.readthedocs.io/en/latest/settings.html#component-split-request"
            )
        return v

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"DjangoGlobalMetadata("
            f"component_split_request={self.component_split_request}, "
            f"oas_version={self.oas_version!r})"
        )


class IRContext(BaseModel):
    """
    Root IR model - single source of truth for code generation.

    This model contains everything needed to generate clients:
    - All schemas (User, UserRequest, PatchedUser, ValidationError, etc.)
    - All operations (users_list, users_create, users_retrieve, etc.)
    - Django metadata (COMPONENT_SPLIT_REQUEST validation)
    - OpenAPI metadata (version, title, servers)

    Examples:
        >>> # Complete API representation
        >>> context = IRContext(
        ...     openapi_info=OpenAPIInfo(
        ...         version="3.1.0",
        ...         title="My Django API",
        ...         api_version="1.0.0",
        ...     ),
        ...     django_metadata=DjangoGlobalMetadata(
        ...         component_split_request=True,
        ...         component_split_patch=True,
        ...     ),
        ...     schemas={
        ...         "User": IRSchemaObject(name="User", type="object", is_response_model=True),
        ...         "UserRequest": IRSchemaObject(name="UserRequest", type="object", is_request_model=True),
        ...         "PatchedUser": IRSchemaObject(name="PatchedUser", type="object", is_patch_model=True),
        ...     },
        ...     operations={
        ...         "users_list": IROperationObject(
        ...             operation_id="users_list",
        ...             http_method="GET",
        ...             path="/api/users/",
        ...             responses={200: IRResponseObject(status_code=200, schema_name="User")},
        ...         ),
        ...         "users_create": IROperationObject(
        ...             operation_id="users_create",
        ...             http_method="POST",
        ...             path="/api/users/",
        ...             request_body=IRRequestBodyObject(schema_name="UserRequest"),
        ...             responses={201: IRResponseObject(status_code=201, schema_name="User")},
        ...         ),
        ...     },
        ... )
        >>> assert context.has_request_response_split
        >>> assert len(context.request_models) == 1
        >>> assert len(context.response_models) == 1
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    # ===== Metadata =====
    openapi_info: OpenAPIInfo = Field(..., description="OpenAPI spec metadata")
    django_metadata: DjangoGlobalMetadata = Field(
        ..., description="Django/drf-spectacular metadata"
    )

    # ===== Schemas =====
    schemas: dict[str, IRSchemaObject] = Field(
        default_factory=dict,
        description="All schemas by name (User, UserRequest, PatchedUser, etc.)",
    )

    # ===== Operations =====
    operations: dict[str, IROperationObject] = Field(
        default_factory=dict,
        description="All operations by operation_id (users_list, users_create, etc.)",
    )

    # ===== Computed Properties =====

    @property
    def has_request_response_split(self) -> bool:
        """
        Check if API uses Request/Response split (COMPONENT_SPLIT_REQUEST: True).

        Returns:
            True if any schema is marked as request model.
        """
        return any(schema.is_request_model for schema in self.schemas.values())

    @property
    def request_models(self) -> dict[str, IRSchemaObject]:
        """Get all request models (UserRequest, TaskRequest, etc.)."""
        return {
            name: schema
            for name, schema in self.schemas.items()
            if schema.is_request_model
        }

    @property
    def response_models(self) -> dict[str, IRSchemaObject]:
        """Get all response models (User, Task, etc.)."""
        return {
            name: schema
            for name, schema in self.schemas.items()
            if schema.is_response_model and not schema.is_patch_model and not schema.is_request_model
        }

    @property
    def patch_models(self) -> dict[str, IRSchemaObject]:
        """Get all PATCH models (PatchedUser, PatchedTask, etc.)."""
        return {
            name: schema
            for name, schema in self.schemas.items()
            if schema.is_patch_model
        }

    @property
    def enum_schemas(self) -> dict[str, IRSchemaObject]:
        """Get all schemas with x-enum-varnames support."""
        return {
            name: schema
            for name, schema in self.schemas.items()
            if schema.has_enum
        }

    @property
    def operations_by_tag(self) -> dict[str, list[IROperationObject]]:
        """Group operations by tags."""
        result: dict[str, list[IROperationObject]] = {}
        for operation in self.operations.values():
            for tag in operation.tags:
                if tag not in result:
                    result[tag] = []
                result[tag].append(operation)
        return result

    @property
    def list_operations(self) -> dict[str, IROperationObject]:
        """Get all list operations (GET endpoints with pagination)."""
        return {
            op_id: op
            for op_id, op in self.operations.items()
            if op.is_list_operation
        }

    @property
    def create_operations(self) -> dict[str, IROperationObject]:
        """Get all create operations (POST endpoints)."""
        return {
            op_id: op for op_id, op in self.operations.items() if op.is_create_operation
        }

    @property
    def retrieve_operations(self) -> dict[str, IROperationObject]:
        """Get all retrieve operations (GET /{id}/ endpoints)."""
        return {
            op_id: op
            for op_id, op in self.operations.items()
            if op.is_retrieve_operation
        }

    @property
    def update_operations(self) -> dict[str, IROperationObject]:
        """Get all update operations (PUT endpoints)."""
        return {
            op_id: op for op_id, op in self.operations.items() if op.is_update_operation
        }

    @property
    def partial_update_operations(self) -> dict[str, IROperationObject]:
        """Get all partial update operations (PATCH endpoints)."""
        return {
            op_id: op
            for op_id, op in self.operations.items()
            if op.is_partial_update_operation
        }

    @property
    def delete_operations(self) -> dict[str, IROperationObject]:
        """Get all delete operations (DELETE endpoints)."""
        return {
            op_id: op for op_id, op in self.operations.items() if op.is_delete_operation
        }

    def get_schema(self, name: str) -> IRSchemaObject | None:
        """Get schema by name."""
        return self.schemas.get(name)

    def get_operation(self, operation_id: str) -> IROperationObject | None:
        """Get operation by operation_id."""
        return self.operations.get(operation_id)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"IRContext("
            f"schemas={len(self.schemas)}, "
            f"operations={len(self.operations)}, "
            f"request_models={len(self.request_models)}, "
            f"response_models={len(self.response_models)})"
        )
