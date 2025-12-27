"""
Service Registry Manager.

Provides business logic for accessing and managing registered gRPC services.
Acts as a bridge between the running gRPC server and the REST API.
"""

from typing import Dict, List, Optional

from django.db import models
from django.db.models import Avg, Count

from ...models import GRPCRequestLog, GRPCServerStatus
from django_cfg.utils import get_logger

from .statistics import (
    calculate_percentiles,
    get_service_statistics,
    aget_service_statistics,
    get_method_statistics,
    aget_method_statistics,
)

logger = get_logger("grpc.service_registry")


class ServiceRegistryManager:
    """
    Manager for accessing registered gRPC services.

    This class provides methods to retrieve service metadata from the running
    gRPC server instance stored in the database.

    Example:
        >>> manager = ServiceRegistryManager()
        >>> services = manager.get_all_services()
        >>> service = manager.get_service_by_name("apps.CryptoService")
    """

    def get_current_server(self) -> Optional[GRPCServerStatus]:
        """Get the currently running gRPC server instance (SYNC)."""
        try:
            current_server = GRPCServerStatus.objects.get_current_server()
            if current_server and current_server.is_running:
                return current_server
            return None
        except Exception as e:
            logger.error(f"Error getting current server: {e}", exc_info=True)
            return None

    async def aget_current_server(self) -> Optional[GRPCServerStatus]:
        """Get the currently running gRPC server instance (ASYNC)."""
        try:
            current_server = await GRPCServerStatus.objects.aget_current_server()
            if current_server and current_server.is_running:
                return current_server
            return None
        except Exception as e:
            logger.error(f"Error getting current server: {e}", exc_info=True)
            return None

    def get_all_services(self) -> List[Dict]:
        """Get all registered services."""
        current_server = self.get_current_server()

        if current_server and current_server.registered_services:
            return current_server.registered_services

        logger.debug("Server not running - discovering services from filesystem")
        from .service_discovery import ServiceDiscovery
        discovery = ServiceDiscovery()
        return discovery.get_registered_services()

    def get_service_by_name(self, service_name: str) -> Optional[Dict]:
        """Get service metadata by service name."""
        services = self.get_all_services()
        return next((s for s in services if s.get("name") == service_name), None)

    def get_service_statistics(self, service_name: str, hours: int = 24) -> Dict:
        """Get statistics for a specific service (SYNC)."""
        return get_service_statistics(service_name, hours)

    async def aget_service_statistics(self, service_name: str, hours: int = 24) -> Dict:
        """Get statistics for a specific service (ASYNC)."""
        return await aget_service_statistics(service_name, hours)

    def get_all_services_with_stats(self, hours: int = 24) -> List[Dict]:
        """Get all services with their statistics (SYNC)."""
        services = self.get_all_services()
        services_with_stats = []

        for service in services:
            service_name = service.get("name")
            stats = self._get_service_summary_stats(service_name, hours)
            service_summary = self._build_service_summary(service, service_name, stats)
            services_with_stats.append(service_summary)

        return services_with_stats

    async def aget_all_services_with_stats(self, hours: int = 24) -> List[Dict]:
        """Get all services with their statistics (ASYNC)."""
        services = self.get_all_services()
        services_with_stats = []

        for service in services:
            service_name = service.get("name")
            stats = await self._aget_service_summary_stats(service_name, hours)
            service_summary = self._build_service_summary(service, service_name, stats)
            services_with_stats.append(service_summary)

        return services_with_stats

    def get_service_methods_with_stats(self, service_name: str) -> List[Dict]:
        """Get all methods for a service with statistics (SYNC)."""
        service = self.get_service_by_name(service_name)
        if not service:
            return []

        methods_list = []
        for method_name in service.get("methods", []):
            method_stats = get_method_statistics(service_name, method_name)
            method_summary = self._build_method_summary(service_name, method_name, method_stats)
            methods_list.append(method_summary)

        return methods_list

    async def aget_service_methods_with_stats(self, service_name: str) -> List[Dict]:
        """Get all methods for a service with statistics (ASYNC)."""
        service = self.get_service_by_name(service_name)
        if not service:
            return []

        methods_list = []
        for method_name in service.get("methods", []):
            method_stats = await aget_method_statistics(service_name, method_name)
            method_summary = self._build_method_summary(service_name, method_name, method_stats)
            methods_list.append(method_summary)

        return methods_list

    def is_server_running(self) -> bool:
        """Check if gRPC server is currently running."""
        return self.get_current_server() is not None

    # Helper methods

    def _get_service_summary_stats(self, service_name: str, hours: int) -> Dict:
        """Get summary stats for a service (SYNC)."""
        return (
            GRPCRequestLog.objects.filter(service_name=service_name)
            .recent(hours)
            .aggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                avg_duration=Avg("duration_ms"),
                last_activity=models.Max("created_at"),
            )
        )

    async def _aget_service_summary_stats(self, service_name: str, hours: int) -> Dict:
        """Get summary stats for a service (ASYNC)."""
        return await (
            GRPCRequestLog.objects.filter(service_name=service_name)
            .recent(hours)
            .aaggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                avg_duration=Avg("duration_ms"),
                last_activity=models.Max("created_at"),
            )
        )

    def _build_service_summary(self, service: Dict, service_name: str, stats: Dict) -> Dict:
        """Build service summary dict."""
        total = stats["total"] or 0
        successful = stats["successful"] or 0
        success_rate = (successful / total * 100) if total > 0 else 0.0
        package = service_name.split(".")[0] if "." in service_name else ""

        return {
            "name": service_name,
            "full_name": service.get("full_name", f"/{service_name}"),
            "package": package,
            "methods_count": len(service.get("methods", [])),
            "total_requests": total,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
            "last_activity_at": (
                stats["last_activity"].isoformat()
                if stats["last_activity"]
                else None
            ),
        }

    def _build_method_summary(self, service_name: str, method_name: str, stats: Dict) -> Dict:
        """Build method summary dict."""
        return {
            "name": method_name,
            "full_name": f"/{service_name}/{method_name}",
            "service_name": service_name,
            "request_type": "",
            "response_type": "",
            "stats": stats,
        }


__all__ = ["ServiceRegistryManager"]
