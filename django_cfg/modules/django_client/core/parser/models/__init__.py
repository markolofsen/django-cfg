"""
OpenAPI Input Models - Pydantic 2 models for raw OpenAPI specs.

These models represent the OpenAPI specification structure as it appears
in JSON/YAML files, before normalization to IR.

Supports both OpenAPI 3.0.3 and 3.1.0.

Usage:
    >>> from django_cfg.modules.django_client.core.parser.models import OpenAPISpec
    >>> spec = OpenAPISpec.model_validate(openapi_dict)
    >>> spec.openapi_version
    '3.1.0'
    >>> spec.all_schema_names
    ['User', 'UserRequest', 'PatchedUser', ...]
"""

from .base import (
    ContactObject,
    ExampleObject,
    ExternalDocumentationObject,
    InfoObject,
    LicenseObject,
    LinkObject,
    ReferenceObject,
    ServerObject,
    ServerVariableObject,
    TagObject,
)
from .components import ComponentsObject, SecuritySchemeObject
from .openapi import OpenAPISpec
from .operation import (
    CallbackObject,
    EncodingObject,
    MediaTypeObject,
    OperationObject,
    ParameterObject,
    PathItemObject,
    RequestBodyObject,
    ResponseObject,
)
from .schema import Discriminator, SchemaObject, XMLObject

__all__ = [
    # Root
    "OpenAPISpec",
    # Base
    "InfoObject",
    "ContactObject",
    "LicenseObject",
    "ServerObject",
    "ServerVariableObject",
    "TagObject",
    "ExternalDocumentationObject",
    "ReferenceObject",
    "ExampleObject",
    "LinkObject",
    # Schema
    "SchemaObject",
    "Discriminator",
    "XMLObject",
    # Operation
    "ParameterObject",
    "MediaTypeObject",
    "EncodingObject",
    "RequestBodyObject",
    "ResponseObject",
    "OperationObject",
    "PathItemObject",
    "CallbackObject",
    # Components
    "ComponentsObject",
    "SecuritySchemeObject",
]
