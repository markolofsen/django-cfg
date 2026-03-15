"""
Proto Generator Module - Protocol Buffer/gRPC code generation.

Generates .proto files from OpenAPI/IR for gRPC client generation.
"""

from .generator import ProtoGenerator
from .messages_generator import ProtoMessagesGenerator
from .services_generator import ProtoServicesGenerator
from .type_mapper import ProtoTypeMapper
from . import naming

__all__ = [
    "ProtoGenerator",
    "ProtoTypeMapper",
    "ProtoMessagesGenerator",
    "ProtoServicesGenerator",
    "naming",
]
