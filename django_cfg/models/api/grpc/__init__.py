"""
gRPC configuration models.

Type-safe Pydantic v2 models for gRPC integration.

Requires: pip install django-cfg[grpc]

Example:
    Flat API (recommended - no nested config imports needed):
    >>> from django_cfg import GRPCConfig
    >>> config = GRPCConfig(
    ...     enabled=True,
    ...     enabled_apps=["crypto"],
    ...     port=50051,
    ...     package_prefix="api",
    ... )

    Advanced with nested configs:
    >>> from django_cfg import GRPCServerConfig, GRPCKeepaliveConfig
    >>> config = GRPCConfig(
    ...     enabled=True,
    ...     server=GRPCServerConfig(
    ...         keepalive=GRPCKeepaliveConfig.for_streaming(),
    ...     ),
    ... )
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import (
        GRPCConfig,
        GRPCServerConfig,
        GRPCKeepaliveConfig,
        GRPCConnectionLimitsConfig,
        GRPCObservabilityConfig,
    )

__all__ = [
    "GRPCConfig",
    "GRPCServerConfig",
    "GRPCKeepaliveConfig",
    "GRPCConnectionLimitsConfig",
    "GRPCObservabilityConfig",
]


def __getattr__(name: str):
    """Lazy import with helpful error message."""
    if name in __all__:
        try:
            from .config import (
                GRPCConfig,
                GRPCServerConfig,
                GRPCKeepaliveConfig,
                GRPCConnectionLimitsConfig,
                GRPCObservabilityConfig,
            )

            return {
                "GRPCConfig": GRPCConfig,
                "GRPCServerConfig": GRPCServerConfig,
                "GRPCKeepaliveConfig": GRPCKeepaliveConfig,
                "GRPCConnectionLimitsConfig": GRPCConnectionLimitsConfig,
                "GRPCObservabilityConfig": GRPCObservabilityConfig,
            }[name]

        except ImportError as e:
            raise ImportError(
                f"gRPC support requires additional dependencies. "
                f"Install with: pip install django-cfg[grpc]\n"
                f"Missing module: {e.name}"
            ) from e

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
