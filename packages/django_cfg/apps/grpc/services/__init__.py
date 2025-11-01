"""
gRPC services utilities.

Provides service discovery and base classes for gRPC services.
"""

from .base import AuthRequiredService, BaseService, ReadOnlyService
from .discovery import ServiceDiscovery, discover_and_register_services

__all__ = [
    "BaseService",
    "ReadOnlyService",
    "AuthRequiredService",
    "ServiceDiscovery",
    "discover_and_register_services",
]
