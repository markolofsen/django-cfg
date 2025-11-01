"""
gRPC authentication components.

Provides JWT authentication for gRPC services.
"""

from .jwt_auth import JWTAuthInterceptor

__all__ = ["JWTAuthInterceptor"]
