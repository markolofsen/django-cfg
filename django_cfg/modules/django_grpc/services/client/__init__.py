"""django_grpc.services.client — gRPC client utilities."""

from .internal_interceptor import InternalSecretClientInterceptor

__all__ = ["InternalSecretClientInterceptor"]
