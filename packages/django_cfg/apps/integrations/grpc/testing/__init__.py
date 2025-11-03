"""
Testing utilities for gRPC services.

Provides example payloads and testing helpers for gRPC methods.
"""

from .examples import EXAMPLES_REGISTRY, get_example

__all__ = [
    "EXAMPLES_REGISTRY",
    "get_example",
]
