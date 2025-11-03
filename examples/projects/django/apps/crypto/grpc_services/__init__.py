"""
Crypto gRPC Services Package.

This package demonstrates complete gRPC integration with django-cfg:
- crypto_service.py: Main gRPC service implementation
- converters.py: Protobuf ↔ Django ORM converters
- client.py: Example gRPC client

Auto-discovered by django-cfg when GRPCConfig.enabled_apps includes "crypto"
"""

from .crypto_service import CryptoService, grpc_handlers
from .converters import ProtobufConverter

__all__ = [
    'CryptoService',
    'grpc_handlers',
    'ProtobufConverter',
]
