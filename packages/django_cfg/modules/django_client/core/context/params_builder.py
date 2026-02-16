"""
Unified Parameter Builder for Operation Code Generation.

Pre-computes all parameter-related values needed by generators.
Eliminates duplicated parameter handling logic across language generators.

Usage:
    from django_cfg.modules.django_client.core.context import ParamsBuilder

    builder = ParamsBuilder(operation)

    # Get context for specific language
    py_ctx = builder.for_python()
    ts_ctx = builder.for_typescript()
    go_ctx = builder.for_go()
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..types import FieldType, TypeMapper
from ..utils import header_to_param_name

if TYPE_CHECKING:
    from ..ir import IROperationObject, IRParameterObject, IRRequestBodyObject


@dataclass(frozen=True, slots=True)
class ParamContext:
    """
    Pre-computed parameter context for templates.

    Contains all values needed to render a parameter in any language.
    """

    # === Identity ===
    name: str
    location: str  # path, query, header, cookie

    # === Types ===
    schema_type: str  # OpenAPI type
    python_type: str
    ts_type: str
    go_type: str
    proto_type: str

    # === Required/Optional ===
    required: bool
    has_default: bool
    default: Any | None

    # === Validation ===
    enum: list[Any] | None
    pattern: str | None
    min_length: int | None
    max_length: int | None
    minimum: float | None
    maximum: float | None

    # === Array ===
    is_array: bool
    items_type: str | None

    # === Metadata ===
    description: str | None
    deprecated: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for template context."""
        return {
            "name": self.name,
            "location": self.location,
            "schema_type": self.schema_type,
            "python_type": self.python_type,
            "ts_type": self.ts_type,
            "go_type": self.go_type,
            "proto_type": self.proto_type,
            "required": self.required,
            "has_default": self.has_default,
            "default": self.default,
            "enum": self.enum,
            "pattern": self.pattern,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "is_array": self.is_array,
            "items_type": self.items_type,
            "description": self.description,
            "deprecated": self.deprecated,
        }


@dataclass(frozen=True, slots=True)
class BodyContext:
    """
    Pre-computed request body context for templates.
    """

    schema_name: str
    content_type: str
    required: bool
    description: str | None

    # Computed
    is_json: bool
    is_multipart: bool
    is_binary: bool
    is_form_urlencoded: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for template context."""
        return {
            "schema_name": self.schema_name,
            "content_type": self.content_type,
            "required": self.required,
            "description": self.description,
            "is_json": self.is_json,
            "is_multipart": self.is_multipart,
            "is_binary": self.is_binary,
            "is_form_urlencoded": self.is_form_urlencoded,
        }


@dataclass(frozen=True, slots=True)
class OperationParamsContext:
    """
    Complete parameter context for an operation.

    Used by all language generators (Python, TypeScript, Go, etc.)
    """

    # === Parameters by location ===
    path_params: tuple[ParamContext, ...]
    query_params: tuple[ParamContext, ...]
    header_params: tuple[ParamContext, ...]
    cookie_params: tuple[ParamContext, ...]

    # === Request body ===
    body: BodyContext | None
    patch_body: BodyContext | None

    # === Computed flags ===
    has_path_params: bool
    has_query_params: bool
    has_header_params: bool
    has_body: bool
    has_required_params: bool
    has_optional_params: bool

    # === Sorted for signatures (required first, then optional) ===
    all_params_sorted: tuple[ParamContext, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for template context."""
        return {
            "path_params": [p.to_dict() for p in self.path_params],
            "query_params": [p.to_dict() for p in self.query_params],
            "header_params": [p.to_dict() for p in self.header_params],
            "cookie_params": [p.to_dict() for p in self.cookie_params],
            "body": self.body.to_dict() if self.body else None,
            "patch_body": self.patch_body.to_dict() if self.patch_body else None,
            "has_path_params": self.has_path_params,
            "has_query_params": self.has_query_params,
            "has_header_params": self.has_header_params,
            "has_body": self.has_body,
            "has_required_params": self.has_required_params,
            "has_optional_params": self.has_optional_params,
            "all_params_sorted": [p.to_dict() for p in self.all_params_sorted],
        }


class ParamsBuilder:
    """
    Unified parameter builder for all language generators.

    Parses IROperationObject and provides pre-computed contexts
    for Python, TypeScript, Go, and other languages.
    """

    def __init__(self, operation: IROperationObject):
        """
        Initialize builder with operation.

        Args:
            operation: IR operation object to build params for
        """
        self.operation = operation
        self._mapper = TypeMapper()
        self._context = self._build_context()

    def _build_context(self) -> OperationParamsContext:
        """Build complete parameter context."""
        # Build param contexts by location
        path_params = []
        query_params = []
        header_params = []
        cookie_params = []

        for param in self.operation.parameters:
            ctx = self._build_param_context(param)
            if param.location == "path":
                path_params.append(ctx)
            elif param.location == "query":
                query_params.append(ctx)
            elif param.location == "header":
                header_params.append(ctx)
            elif param.location == "cookie":
                cookie_params.append(ctx)

        # Build body contexts
        body = self._build_body_context(self.operation.request_body) if self.operation.request_body else None
        patch_body = self._build_body_context(self.operation.patch_request_body) if self.operation.patch_request_body else None

        # Sort all params: required first, then optional
        all_params = path_params + query_params + header_params + cookie_params
        required = [p for p in all_params if p.required]
        optional = [p for p in all_params if not p.required]
        all_sorted = required + optional

        return OperationParamsContext(
            path_params=tuple(path_params),
            query_params=tuple(query_params),
            header_params=tuple(header_params),
            cookie_params=tuple(cookie_params),
            body=body,
            patch_body=patch_body,
            has_path_params=bool(path_params),
            has_query_params=bool(query_params),
            has_header_params=bool(header_params),
            has_body=body is not None or patch_body is not None,
            has_required_params=bool(required),
            has_optional_params=bool(optional),
            all_params_sorted=tuple(all_sorted),
        )

    def _build_param_context(self, param: IRParameterObject) -> ParamContext:
        """Build context for single parameter."""
        # Determine field type
        try:
            ft = FieldType(param.schema_type)
        except ValueError:
            ft = FieldType.STRING

        # Get types for each language
        python_type = self._get_python_type(param)
        ts_type = self._get_ts_type(param)
        go_type = self._mapper.to_go(ft, optional=not param.required)
        proto_type = self._mapper.to_proto(ft)

        return ParamContext(
            name=param.name,
            location=param.location,
            schema_type=param.schema_type,
            python_type=python_type,
            ts_type=ts_type,
            go_type=go_type,
            proto_type=proto_type,
            required=param.required,
            has_default=param.default is not None,
            default=param.default,
            enum=list(param.enum) if param.enum else None,
            pattern=param.pattern,
            min_length=param.min_length,
            max_length=param.max_length,
            minimum=param.minimum,
            maximum=param.maximum,
            is_array=param.schema_type == "array",
            items_type=param.items_type,
            description=param.description,
            deprecated=param.deprecated,
        )

    def _build_body_context(self, body: IRRequestBodyObject) -> BodyContext:
        """Build context for request body."""
        content_type = body.content_type

        return BodyContext(
            schema_name=body.schema_name,
            content_type=content_type,
            required=body.required,
            description=body.description,
            is_json=content_type == "application/json",
            is_multipart=content_type == "multipart/form-data",
            is_binary=content_type == "application/octet-stream",
            is_form_urlencoded=content_type == "application/x-www-form-urlencoded",
        )

    def _get_python_type(self, param: IRParameterObject) -> str:
        """Get Python type for parameter."""
        type_map = {
            "string": "str",
            "integer": "int",
            "number": "float",
            "boolean": "bool",
            "array": f"list[{param.items_type or 'Any'}]",
        }
        base_type = type_map.get(param.schema_type, "Any")
        if not param.required:
            return f"{base_type} | None"
        return base_type

    def _get_ts_type(self, param: IRParameterObject) -> str:
        """Get TypeScript type for parameter."""
        type_map = {
            "string": "string",
            "integer": "number",
            "number": "number",
            "boolean": "boolean",
            "array": f"Array<{param.items_type or 'any'}>",
        }
        base_type = type_map.get(param.schema_type, "any")
        # TypeScript uses ? for optional, not union with undefined in params
        return base_type

    @property
    def context(self) -> OperationParamsContext:
        """Get the complete parameter context."""
        return self._context

    def to_dict(self) -> dict[str, Any]:
        """Get context as dictionary for templates."""
        return self._context.to_dict()

    # === Language-specific contexts ===

    def for_python(self) -> dict[str, Any]:
        """
        Get Python-specific parameter context.

        Returns dict with:
        - signature_params: List of "name: type" strings for method signature
        - path_params: Path parameters
        - query_params: Query parameters
        - has_body: Whether operation has request body
        - body_type: Request body schema name
        """
        sig_params = ["self"]

        # Path params first (always required)
        for p in self._context.path_params:
            sig_params.append(f"{p.name}: {p.python_type}")

        # Body param
        if self._context.body:
            sig_params.append(f"data: {self._context.body.schema_name}")
        elif self._context.patch_body:
            sig_params.append(f"data: {self._context.patch_body.schema_name} | None = None")

        # Query params (required first, then optional)
        for p in self._context.query_params:
            if p.required:
                sig_params.append(f"{p.name}: {p.python_type}")
        for p in self._context.query_params:
            if not p.required:
                sig_params.append(f"{p.name}: {p.python_type} = None")

        # Header params (required first, then optional)
        for p in self._context.header_params:
            if p.required:
                sig_params.append(f"{p.name}: {p.python_type}")
        for p in self._context.header_params:
            if not p.required:
                sig_params.append(f"{p.name}: {p.python_type} = None")

        return {
            "signature_params": sig_params,
            "signature": ", ".join(sig_params),
            "path_params": [p.to_dict() for p in self._context.path_params],
            "query_params": [p.to_dict() for p in self._context.query_params],
            "header_params": [p.to_dict() for p in self._context.header_params],
            "has_body": self._context.has_body,
            "body": self._context.body.to_dict() if self._context.body else None,
            "patch_body": self._context.patch_body.to_dict() if self._context.patch_body else None,
            "has_query_params": self._context.has_query_params,
            "has_header_params": self._context.has_header_params,
        }

    def for_typescript(self) -> dict[str, Any]:
        """
        Get TypeScript-specific parameter context.

        Returns dict with:
        - signature_params: List of "name: type" or "name?: type" strings
        - path_params: Path parameters
        - query_params: Query parameters
        - has_body: Whether operation has request body
        - body_type: Request body schema name
        """
        sig_params = []

        # Path params first (always required)
        for p in self._context.path_params:
            sig_params.append(f"{p.name}: {p.ts_type}")

        # Body param
        if self._context.body:
            sig_params.append(f"data: {self._context.body.schema_name}")
        elif self._context.patch_body:
            sig_params.append(f"data?: {self._context.patch_body.schema_name}")

        # Header params (required first, then optional)
        for p in self._context.header_params:
            if p.required:
                sig_params.append(f"{header_to_param_name(p.name)}: {p.ts_type}")
        for p in self._context.header_params:
            if not p.required:
                sig_params.append(f"{header_to_param_name(p.name)}?: {p.ts_type}")

        # Query params (required first, then optional)
        for p in self._context.query_params:
            if p.required:
                sig_params.append(f"{p.name}: {p.ts_type}")
        for p in self._context.query_params:
            if not p.required:
                sig_params.append(f"{p.name}?: {p.ts_type}")

        return {
            "signature_params": sig_params,
            "signature": ", ".join(sig_params),
            "path_params": [p.to_dict() for p in self._context.path_params],
            "query_params": [p.to_dict() for p in self._context.query_params],
            "header_params": [p.to_dict() for p in self._context.header_params],
            "has_body": self._context.has_body,
            "body": self._context.body.to_dict() if self._context.body else None,
            "patch_body": self._context.patch_body.to_dict() if self._context.patch_body else None,
            "has_query_params": self._context.has_query_params,
            "has_header_params": self._context.has_header_params,
        }

    def for_go(self) -> dict[str, Any]:
        """
        Get Go-specific parameter context.

        Returns dict with Go-style signatures and types.
        """
        sig_params = ["ctx context.Context"]

        # Path params
        for p in self._context.path_params:
            sig_params.append(f"{p.name} {p.go_type}")

        # Body param
        if self._context.body:
            sig_params.append(f"data *{self._context.body.schema_name}")
        elif self._context.patch_body:
            sig_params.append(f"data *{self._context.patch_body.schema_name}")

        # Query params (use opts pattern for optional)
        # In Go, optional params often go into Options struct

        return {
            "signature_params": sig_params,
            "signature": ", ".join(sig_params),
            "path_params": [p.to_dict() for p in self._context.path_params],
            "query_params": [p.to_dict() for p in self._context.query_params],
            "has_body": self._context.has_body,
            "body": self._context.body.to_dict() if self._context.body else None,
            "has_query_params": self._context.has_query_params,
            "needs_context_import": True,
        }

    # Note: _to_camel_case removed - use header_to_param_name from utils
