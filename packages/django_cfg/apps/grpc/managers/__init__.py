"""
Managers for gRPC app models.
"""

from .grpc_request_log import GRPCRequestLogManager, GRPCRequestLogQuerySet

__all__ = [
    "GRPCRequestLogManager",
    "GRPCRequestLogQuerySet",
]
