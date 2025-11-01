"""
Admin interface for gRPC app.
"""

from .config import grpcrequestlog_config
from .grpc_request_log import GRPCRequestLogAdmin

__all__ = [
    "GRPCRequestLogAdmin",
    "grpcrequestlog_config",
]
