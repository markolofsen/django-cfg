"""
Utilities for gRPC Integration.

Reusable utilities for gRPC services in django-cfg.
"""

from .streaming_logger import setup_streaming_logger, get_streaming_logger

__all__ = ["setup_streaming_logger", "get_streaming_logger"]
