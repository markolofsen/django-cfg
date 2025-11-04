"""
gRPC authentication components.

Provides API key authentication for gRPC services.
"""

from .api_key_auth import ApiKeyAuthInterceptor

__all__ = ["ApiKeyAuthInterceptor"]
