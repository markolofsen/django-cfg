"""
IR Operation Models - Type-safe API endpoint representation.

This module defines operations (endpoints) with Request/Response split awareness,
supporting Django-specific patterns from drf-spectacular.

Key Features:
- Separate request_body and patch_request_body (COMPONENT_SPLIT_PATCH)
- Multiple response schemas (200, 201, 400, 404, etc.)
- Path/query/header/cookie parameters
- Django metadata (authentication, permissions, csrf)
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class IRParameterObject(BaseModel):
    """
    API parameter (path, query, header, cookie).

    Examples:
        >>> # Path parameter
        >>> user_id = IRParameterObject(
        ...     name="id",
        ...     location="path",
        ...     schema_type="integer",
        ...     required=True,
        ...     description="User ID",
        ... )

        >>> # Query parameter with default
        >>> page_size = IRParameterObject(
        ...     name="page_size",
        ...     location="query",
        ...     schema_type="integer",
        ...     required=False,
        ...     default=20,
        ...     description="Items per page",
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    name: str = Field(..., description="Parameter name (e.g., 'id', 'page_size')")
    location: Literal["path", "query", "header", "cookie"] = Field(
        ..., description="Parameter location"
    )
    schema_type: str = Field(
        ...,
        description="Parameter type: string, integer, number, boolean, array",
    )
    required: bool = Field(False, description="Is parameter required")
    description: str | None = Field(None, description="Parameter description")

    # Validation
    default: Any | None = Field(None, description="Default value")
    enum: list[str | int | float] | None = Field(
        None, description="Allowed values"
    )
    pattern: str | None = Field(None, description="Regex pattern (for strings)")
    min_length: int | None = Field(None, ge=0, description="Minimum string length")
    max_length: int | None = Field(None, ge=0, description="Maximum string length")
    minimum: int | float | None = Field(None, description="Minimum numeric value")
    maximum: int | float | None = Field(None, description="Maximum numeric value")

    # Array support
    items_type: str | None = Field(
        None,
        description="Array item type (for schema_type='array')",
    )

    deprecated: bool = Field(False, description="Is parameter deprecated")

    @property
    def python_type(self) -> str:
        """
        Get Python type hint for this parameter.

        Examples:
            >>> IRParameterObject(name="id", location="path", schema_type="integer", required=True).python_type
            'int'
            >>> IRParameterObject(name="tags", location="query", schema_type="array", items_type="string", required=False).python_type
            'list[str] | None'
        """
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": f"list[{self.items_type or 'Any'}]",
        }

        base_type = type_map.get(self.schema_type, "Any")

        if not self.required:
            return f"{base_type} | None"

        return base_type

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = [
            f"IRParameterObject(name={self.name!r}",
            f"location={self.location!r}",
            f"schema_type={self.schema_type!r}",
        ]

        if self.required:
            parts.append("required=True")

        if self.default is not None:
            parts.append(f"default={self.default!r}")

        return ", ".join(parts) + ")"


class IRRequestBodyObject(BaseModel):
    """
    Request body schema reference.

    Examples:
        >>> # POST /users/ (UserRequest)
        >>> post_body = IRRequestBodyObject(
        ...     schema_name="UserRequest",
        ...     content_type="application/json",
        ...     required=True,
        ... )

        >>> # PATCH /users/{id}/ (PatchedUser)
        >>> patch_body = IRRequestBodyObject(
        ...     schema_name="PatchedUser",
        ...     content_type="application/json",
        ...     required=False,
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    schema_name: str = Field(
        ..., description="Schema reference (e.g., 'UserRequest', 'PatchedUser')"
    )
    content_type: str = Field(
        "application/json",
        description="Content type (application/json, multipart/form-data, etc.)",
    )
    required: bool = Field(True, description="Is request body required")
    description: str | None = Field(None, description="Request body description")

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = [
            f"IRRequestBodyObject(schema_name={self.schema_name!r}",
            f"content_type={self.content_type!r}",
        ]

        if not self.required:
            parts.append("required=False")

        return ", ".join(parts) + ")"


class IRResponseObject(BaseModel):
    """
    Response schema with status code.

    Examples:
        >>> # 200 OK (User)
        >>> success = IRResponseObject(
        ...     status_code=200,
        ...     schema_name="User",
        ...     description="User retrieved successfully",
        ... )

        >>> # 201 Created (User)
        >>> created = IRResponseObject(
        ...     status_code=201,
        ...     schema_name="User",
        ...     description="User created successfully",
        ... )

        >>> # 400 Bad Request (ValidationError)
        >>> error = IRResponseObject(
        ...     status_code=400,
        ...     schema_name="ValidationError",
        ...     description="Invalid request data",
        ... )

        >>> # 204 No Content (no schema)
        >>> no_content = IRResponseObject(
        ...     status_code=204,
        ...     schema_name=None,
        ...     description="Deleted successfully",
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    status_code: int = Field(
        ..., ge=100, le=599, description="HTTP status code (200, 201, 400, etc.)"
    )
    schema_name: str | None = Field(
        None, description="Response schema name (e.g., 'User', 'ValidationError')"
    )
    content_type: str = Field(
        "application/json",
        description="Response content type",
    )
    description: str | None = Field(None, description="Response description")

    # Pagination (for list endpoints)
    is_paginated: bool = Field(
        False, description="Is response paginated (PageNumberPagination)"
    )

    @property
    def is_success(self) -> bool:
        """Check if response is successful (2xx)."""
        return 200 <= self.status_code < 300

    @property
    def is_error(self) -> bool:
        """Check if response is error (4xx, 5xx)."""
        return self.status_code >= 400

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = [
            f"IRResponseObject(status_code={self.status_code}",
        ]

        if self.schema_name:
            parts.append(f"schema_name={self.schema_name!r}")

        if self.is_paginated:
            parts.append("is_paginated=True")

        return ", ".join(parts) + ")"


class IROperationObject(BaseModel):
    """
    API operation (endpoint) with Request/Response split awareness.

    This model represents a single API endpoint with full metadata:
    - HTTP method (GET, POST, PUT, PATCH, DELETE)
    - Path and parameters
    - Request body (with separate patch_request_body for PATCH)
    - Multiple responses (200, 201, 400, 404, etc.)
    - Django metadata (authentication, permissions)

    Examples:
        >>> # POST /users/ - Create user
        >>> create_user = IROperationObject(
        ...     operation_id="users_create",
        ...     http_method="POST",
        ...     path="/api/users/",
        ...     summary="Create new user",
        ...     request_body=IRRequestBodyObject(schema_name="UserRequest"),
        ...     responses={
        ...         201: IRResponseObject(status_code=201, schema_name="User"),
        ...         400: IRResponseObject(status_code=400, schema_name="ValidationError"),
        ...     },
        ...     tags=["users"],
        ... )

        >>> # PATCH /users/{id}/ - Partial update
        >>> partial_update = IROperationObject(
        ...     operation_id="users_partial_update",
        ...     http_method="PATCH",
        ...     path="/api/users/{id}/",
        ...     summary="Partial update user",
        ...     parameters=[
        ...         IRParameterObject(name="id", location="path", schema_type="integer", required=True),
        ...     ],
        ...     patch_request_body=IRRequestBodyObject(schema_name="PatchedUser", required=False),
        ...     responses={
        ...         200: IRResponseObject(status_code=200, schema_name="User"),
        ...         404: IRResponseObject(status_code=404, schema_name="Error"),
        ...     },
        ...     tags=["users"],
        ... )

        >>> # GET /users/ - List users (paginated)
        >>> list_users = IROperationObject(
        ...     operation_id="users_list",
        ...     http_method="GET",
        ...     path="/api/users/",
        ...     summary="List users",
        ...     parameters=[
        ...         IRParameterObject(name="page", location="query", schema_type="integer", required=False),
        ...         IRParameterObject(name="page_size", location="query", schema_type="integer", required=False),
        ...     ],
        ...     responses={
        ...         200: IRResponseObject(status_code=200, schema_name="PaginatedUserList", is_paginated=True),
        ...     },
        ...     tags=["users"],
        ... )
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
        validate_default=True,
        str_strip_whitespace=True,
    )

    # ===== Core Fields =====
    operation_id: str = Field(
        ...,
        description="Unique operation ID (e.g., 'users_create', 'tasks_partial_update')",
    )
    http_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"] = (
        Field(..., description="HTTP method")
    )
    path: str = Field(..., description="URL path (e.g., '/api/users/{id}/')")
    summary: str | None = Field(None, description="Operation summary")
    description: str | None = Field(None, description="Detailed description")
    tags: list[str] = Field(
        default_factory=list, description="OpenAPI tags (e.g., ['users', 'auth'])"
    )

    # ===== Parameters =====
    parameters: list[IRParameterObject] = Field(
        default_factory=list,
        description="Path/query/header parameters",
    )

    # ===== Request Bodies (NEW: Separate POST/PUT vs PATCH) =====
    request_body: IRRequestBodyObject | None = Field(
        None,
        description="Request body for POST/PUT (e.g., UserRequest)",
    )
    patch_request_body: IRRequestBodyObject | None = Field(
        None,
        description="Request body for PATCH (e.g., PatchedUser with all optional fields)",
    )

    # ===== Responses =====
    responses: dict[int, IRResponseObject] = Field(
        ...,
        description="Responses by status code (200, 201, 400, 404, etc.)",
    )

    # ===== Django Metadata =====
    authentication_classes: list[str] = Field(
        default_factory=list,
        description="Django authentication classes (e.g., ['SessionAuthentication', 'TokenAuthentication'])",
    )
    permission_classes: list[str] = Field(
        default_factory=list,
        description="Django permission classes (e.g., ['IsAuthenticated', 'IsAdminUser'])",
    )
    csrf_exempt: bool = Field(
        False, description="Is operation CSRF exempt (@csrf_exempt)"
    )

    # ===== Metadata =====
    deprecated: bool = Field(False, description="Is operation deprecated")

    # ===== Computed Properties =====

    @property
    def is_list_operation(self) -> bool:
        """Check if operation is list endpoint (GET with pagination)."""
        if self.http_method != "GET":
            return False

        # Check if primary success response is paginated
        success_response = self.responses.get(200)
        return success_response is not None and success_response.is_paginated

    @property
    def is_retrieve_operation(self) -> bool:
        """Check if operation is retrieve endpoint (GET /{id}/)."""
        return (
            self.http_method == "GET"
            and "{id}" in self.path
            and not self.is_list_operation
        )

    @property
    def is_create_operation(self) -> bool:
        """Check if operation is create endpoint (POST)."""
        return self.http_method == "POST"

    @property
    def is_update_operation(self) -> bool:
        """Check if operation is update endpoint (PUT)."""
        return self.http_method == "PUT"

    @property
    def is_partial_update_operation(self) -> bool:
        """Check if operation is partial update endpoint (PATCH)."""
        return self.http_method == "PATCH"

    @property
    def is_delete_operation(self) -> bool:
        """Check if operation is delete endpoint (DELETE)."""
        return self.http_method == "DELETE"

    @property
    def requires_authentication(self) -> bool:
        """Check if operation requires authentication."""
        return bool(self.authentication_classes)

    @property
    def path_parameters(self) -> list[IRParameterObject]:
        """Get path parameters only."""
        return [p for p in self.parameters if p.location == "path"]

    @property
    def query_parameters(self) -> list[IRParameterObject]:
        """Get query parameters only."""
        return [p for p in self.parameters if p.location == "query"]

    @property
    def header_parameters(self) -> list[IRParameterObject]:
        """Get header parameters only."""
        return [p for p in self.parameters if p.location == "header"]

    @property
    def success_responses(self) -> dict[int, IRResponseObject]:
        """Get successful responses only (2xx)."""
        return {
            status: response
            for status, response in self.responses.items()
            if response.is_success
        }

    @property
    def error_responses(self) -> dict[int, IRResponseObject]:
        """Get error responses only (4xx, 5xx)."""
        return {
            status: response
            for status, response in self.responses.items()
            if response.is_error
        }

    @property
    def primary_success_status(self) -> int:
        """
        Get primary success status code.

        Returns:
            Primary success status (200 for GET/PUT/PATCH, 201 for POST, 204 for DELETE).

        Examples:
            >>> get_op = IROperationObject(operation_id="users_list", http_method="GET", path="/api/users/", responses={200: IRResponseObject(status_code=200)})
            >>> get_op.primary_success_status
            200

            >>> post_op = IROperationObject(operation_id="users_create", http_method="POST", path="/api/users/", responses={201: IRResponseObject(status_code=201)})
            >>> post_op.primary_success_status
            201
        """
        success = self.success_responses
        if not success:
            return 200

        # Prefer 201 for POST, 204 for DELETE, otherwise first 2xx
        if 201 in success:
            return 201
        if 204 in success:
            return 204
        if 200 in success:
            return 200

        return min(success.keys())

    @property
    def primary_success_response(self) -> IRResponseObject | None:
        """Get primary success response object."""
        return self.responses.get(self.primary_success_status)

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = [
            f"IROperationObject(operation_id={self.operation_id!r}",
            f"http_method={self.http_method!r}",
            f"path={self.path!r}",
        ]

        if self.request_body:
            parts.append(
                f"request_body={self.request_body.schema_name!r}"
            )

        if self.patch_request_body:
            parts.append(
                f"patch_request_body={self.patch_request_body.schema_name!r}"
            )

        parts.append(f"responses=[{', '.join(map(str, self.responses.keys()))}]")

        return ", ".join(parts) + ")"
