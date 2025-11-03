"""
gRPC System Configuration.

Internal system utilities for configuration, dependency checking, and validation.
This module is for system/internal use. For public API, use `utils/` instead.
"""

from .dependencies import (
    DependencyChecker,
    GRPCDependencyError,
    check_grpc_available,
    check_grpc_dependencies,
    print_dependency_status,
    require_grpc_feature,
)

__all__ = [
    # Dependency checking
    "DependencyChecker",
    "GRPCDependencyError",
    "check_grpc_available",
    "check_grpc_dependencies",
    "require_grpc_feature",
    "print_dependency_status",
]
