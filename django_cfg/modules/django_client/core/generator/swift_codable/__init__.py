"""
Swift Codable Generator Module - Simple Swift Codable types generation.

Generates plain Swift Codable structs and APIEndpoints from OpenAPI/IR.
No OpenAPIRuntime dependency - just simple, clean Swift code.
"""

from .generator import SwiftCodableGenerator
from .type_mapper import SwiftTypeMapper
from .models_generator import SwiftModelsGenerator
from .endpoints_generator import SwiftEndpointsGenerator
from .naming import (
    to_pascal_case,
    to_camel_case,
    swift_property_name,
    sanitize_swift_identifier,
    SWIFT_KEYWORDS,
)

__all__ = [
    "SwiftCodableGenerator",
    "SwiftTypeMapper",
    "SwiftModelsGenerator",
    "SwiftEndpointsGenerator",
    "to_pascal_case",
    "to_camel_case",
    "swift_property_name",
    "sanitize_swift_identifier",
    "SWIFT_KEYWORDS",
]
