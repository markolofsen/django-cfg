"""
IR (Intermediate Representation) - Unified API representation.

This package defines the version-agnostic, language-agnostic intermediate
representation for Django APIs. All parsers (OpenAPI 3.0.3, 3.1.0) normalize
to this IR, and all generators (Python, TypeScript) consume this IR.

Key Features:
- Request/Response split (UserRequest vs User)
- x-enum-varnames support (strongly typed enums)
- Nullable normalization (both 3.0 and 3.1 → single nullable field)
- Django metadata (COMPONENT_SPLIT_REQUEST validation)

Usage:
    >>> from django_cfg.modules.django_client.core.ir import IRContext, IRSchemaObject, IROperationObject
    >>> # Create schemas
    >>> user_schema = IRSchemaObject(name="User", type="object", is_response_model=True)
    >>> user_request = IRSchemaObject(name="UserRequest", type="object", is_request_model=True)
    >>> # Create operation
    >>> operation = IROperationObject(
    ...     operation_id="users_create",
    ...     http_method="POST",
    ...     path="/api/users/",
    ...     request_body=IRRequestBodyObject(schema_name="UserRequest"),
    ...     responses={201: IRResponseObject(status_code=201, schema_name="User")},
    ... )
    >>> # Create context
    >>> context = IRContext(
    ...     openapi_info=OpenAPIInfo(version="3.1.0", title="My API"),
    ...     django_metadata=DjangoGlobalMetadata(component_split_request=True),
    ...     schemas={"User": user_schema, "UserRequest": user_request},
    ...     operations={"users_create": operation},
    ... )
"""

from .context import DjangoGlobalMetadata, IRContext, OpenAPIInfo
from .operation import (
    IROperationObject,
    IRParameterObject,
    IRRequestBodyObject,
    IRResponseObject,
)
from .schema import IRSchemaObject

__all__ = [
    # Context (root model)
    "IRContext",
    "OpenAPIInfo",
    "DjangoGlobalMetadata",
    # Schema
    "IRSchemaObject",
    # Operation
    "IROperationObject",
    "IRParameterObject",
    "IRRequestBodyObject",
    "IRResponseObject",
]
