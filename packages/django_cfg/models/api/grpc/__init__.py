"""
gRPC configuration models.

Type-safe Pydantic v2 models for gRPC server, authentication, and proto generation.

Requires: pip install django-cfg[grpc]

Example:
    >>> from django_cfg.models.api.grpc import GRPCConfig, GRPCServerConfig
    >>> config = GRPCConfig(
    ...     enabled=True,
    ...     server=GRPCServerConfig(port=50051)
    ... )
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import (
        GRPCAuthConfig,
        GRPCConfig,
        GRPCProtoConfig,
        GRPCServerConfig,
    )

__all__ = [
    "GRPCConfig",
    "GRPCServerConfig",
    "GRPCAuthConfig",
    "GRPCProtoConfig",
]


def __getattr__(name: str):
    """Lazy import with helpful error message."""
    if name in __all__:
        try:
            from .config import (
                GRPCAuthConfig,
                GRPCConfig,
                GRPCProtoConfig,
                GRPCServerConfig,
            )

            return {
                "GRPCConfig": GRPCConfig,
                "GRPCServerConfig": GRPCServerConfig,
                "GRPCAuthConfig": GRPCAuthConfig,
                "GRPCProtoConfig": GRPCProtoConfig,
            }[name]

        except ImportError as e:
            raise ImportError(
                f"gRPC support requires additional dependencies. "
                f"Install with: pip install django-cfg[grpc]\n"
                f"Missing module: {e.name}"
            ) from e

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
