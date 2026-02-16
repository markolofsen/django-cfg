"""
Template Context Builders for Django Client Generator.

Pre-computes all values needed by templates from IR + Smart Detection.
"""

from .field_context import (
    FieldContext,
    SchemaContext,
    build_field_context,
    build_schema_context,
)
from .params_builder import (
    ParamContext,
    BodyContext,
    OperationParamsContext,
    ParamsBuilder,
)

__all__ = [
    # Field context
    "FieldContext",
    "SchemaContext",
    "build_field_context",
    "build_schema_context",
    # Params builder
    "ParamContext",
    "BodyContext",
    "OperationParamsContext",
    "ParamsBuilder",
]
