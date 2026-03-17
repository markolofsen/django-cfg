"""django_grpc.services.discovery — Service discovery and registration."""

from .registration import discover_and_register_services
from .service_discovery import ServiceDiscovery

__all__ = ["ServiceDiscovery", "discover_and_register_services"]
