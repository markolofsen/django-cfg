"""Streamlit Admin services layer.

Business logic services with API client integration.

Note: Services are imported lazily to avoid import errors when
running from scaffold (different sys.path) vs Django package.
"""

from .base import BaseService

# Lazy imports - these may fail when imported as Django package
# but will work when running from scaffold
try:
    from .centrifugo import CentrifugoService
    from .dashboard import DashboardService
    from .grpc import GRPCService
    from .rq import RQService
    from .system import SystemService
    from .users import UsersService
except ImportError:
    # When imported as Django package, services are not needed
    CentrifugoService = None  # type: ignore
    DashboardService = None  # type: ignore
    GRPCService = None  # type: ignore
    RQService = None  # type: ignore
    SystemService = None  # type: ignore
    UsersService = None  # type: ignore

__all__ = [
    "BaseService",
    "DashboardService",
    "RQService",
    "CentrifugoService",
    "GRPCService",
    "UsersService",
    "SystemService",
]
