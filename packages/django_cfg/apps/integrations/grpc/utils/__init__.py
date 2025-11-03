"""
gRPC utilities.

Provides proto generation and other helper utilities for gRPC integration.

Note:
    For dependency checking, use `django_cfg.apps.integrations.grpc._cfg` instead.
    This module focuses on user-facing utilities like proto generation.
"""

from .proto_gen import ProtoFieldMapper, ProtoGenerator, generate_proto_for_app

__all__ = [
    # Proto generation
    "ProtoFieldMapper",
    "ProtoGenerator",
    "generate_proto_for_app",
]
