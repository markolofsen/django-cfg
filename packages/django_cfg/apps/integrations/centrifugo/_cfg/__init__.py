"""
Centrifugo System Configuration.

Internal system utilities for configuration, dependency checking, and validation.
This module is for system/internal use. For public API, use other modules instead.
"""

from .dependencies import (
    CentrifugoDependencyError,
    DependencyChecker,
    check_centrifugo_available,
    check_centrifugo_dependencies,
    print_dependency_status,
    require_centrifugo_feature,
)

__all__ = [
    # Dependency checking
    "DependencyChecker",
    "CentrifugoDependencyError",
    "check_centrifugo_available",
    "check_centrifugo_dependencies",
    "require_centrifugo_feature",
    "print_dependency_status",
]
