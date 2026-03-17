"""
django_grpc — gRPC module for django-cfg.

Async gRPC server with Cloudflare D1 persistence, Redis API key caching,
bidirectional streaming support, and service auto-discovery.

No PostgreSQL required — all state stored in D1.

Usage in djangoconfig.py:
    from django_cfg.modules.django_grpc import DjangoGrpcModuleConfig

    class MyConfig(DjangoConfig):
        grpc_module: DjangoGrpcModuleConfig = DjangoGrpcModuleConfig(
            enabled=True,
            server=GrpcServerConfig(port=50051),
        )

Run server:
    uv run manage.py rungrpc
"""

from __future__ import annotations

default_app_config = "django_cfg.modules.django_grpc.apps.DjangoGrpcConfig"

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .events.service import GrpcD1Service

from .exceptions import DjangoGrpcConfigError, DjangoGrpcError, DjangoGrpcSyncError
from .__cfg__ import DjangoGrpcModuleConfig

# Sub-configs re-exported for direct module-level imports.
# Preferred import path: `from django_cfg import GrpcServerConfig` (via registry).
# These re-exports support `from django_cfg.modules.django_grpc import GrpcServerConfig`.
from .config.server import GrpcServerConfig
from .config.auth import GrpcAuthConfig
from .config.pool import GrpcPoolConfig
from .config.resilience import ResilienceConfig
from .config.observability import ObservabilityConfig
from .config.metrics import MetricsConfig
from .config.tls import TLSConfig

_service_instance: Optional["GrpcD1Service"] = None


def is_enabled() -> bool:
    """Return True when django_cf (D1) is configured and ready."""
    try:
        from django_cfg.modules.django_cf import is_ready
        return is_ready()
    except Exception:
        return False


def get_service() -> "GrpcD1Service":
    """Return (cached) GrpcD1Service instance.

    Raises DjangoGrpcConfigError if django_cf is not configured.
    """
    global _service_instance
    if _service_instance is None:
        if not is_enabled():
            raise DjangoGrpcConfigError(
                "django_grpc: django_cf is not configured",
                suggestion="Add CloudflareConfig(enabled=True, ...) to DjangoConfig",
            )
        from .events.service import GrpcD1Service
        _service_instance = GrpcD1Service()
    return _service_instance


def reset_service() -> None:
    """Reset cached service instance (useful in tests)."""
    global _service_instance
    _service_instance = None


__all__ = [
    # Top-level module config
    "DjangoGrpcModuleConfig",
    # Sub-configs (import from here — no need to dig into config.*)
    "GrpcServerConfig",
    "GrpcAuthConfig",
    "GrpcPoolConfig",
    "ResilienceConfig",
    "ObservabilityConfig",
    "MetricsConfig",
    "TLSConfig",
    # Exceptions
    "DjangoGrpcError",
    "DjangoGrpcConfigError",
    "DjangoGrpcSyncError",
    # Helpers
    "is_enabled",
    "get_service",
    "reset_service",
]
