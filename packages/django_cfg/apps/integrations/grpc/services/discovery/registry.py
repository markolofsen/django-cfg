"""
Service Registry Manager.

Provides business logic for accessing and managing registered gRPC services.
Acts as a bridge between the running gRPC server and the REST API.
"""

from typing import Dict, List, Optional

from django.db import models
from django.db.models import Avg, Count

from ...models import GRPCRequestLog, GRPCServerStatus
from django_cfg.modules.django_logging import get_logger

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
        """
        Get the currently running gRPC server instance (SYNC).

        Returns:
            GRPCServerStatus instance if server is running, None otherwise
        """
        try:
            current_server = GRPCServerStatus.objects.get_current_server()
            if current_server and current_server.is_running:
                return current_server
            return None
        except Exception as e:
            logger.error(f"Error getting current server: {e}", exc_info=True)
            return None

    async def aget_current_server(self) -> Optional[GRPCServerStatus]:
        """
        Get the currently running gRPC server instance (ASYNC - Django 5.2).

        Returns:
            GRPCServerStatus instance if server is running, None otherwise
        """
        try:
            current_server = await GRPCServerStatus.objects.aget_current_server()
            if current_server and current_server.is_running:
                return current_server
            return None
        except Exception as e:
            logger.error(f"Error getting current server: {e}", exc_info=True)
            return None

    def get_all_services(self) -> List[Dict]:
        """
        Get all registered services.

        Returns services from running server if available,
        otherwise discovers services from filesystem.

        Returns:
            List of service metadata dictionaries

        Example:
            >>> manager = ServiceRegistryManager()
            >>> services = manager.get_all_services()
            >>> len(services)
            1
            >>> services[0]['name']
            'apps.CryptoService'
        """
        current_server = self.get_current_server()

        # If server is running, use its registered services
        if current_server and current_server.registered_services:
            return current_server.registered_services

        # Otherwise, discover services from filesystem
        logger.debug("Server not running - discovering services from filesystem")
        from .discovery import ServiceDiscovery
        discovery = ServiceDiscovery()
        return discovery.get_registered_services()

    def get_service_by_name(self, service_name: str) -> Optional[Dict]:
        """
        Get service metadata by service name.

        Args:
            service_name: Full service name (e.g., "apps.CryptoService")

        Returns:
            Service metadata dictionary or None if not found

        Example:
            >>> manager = ServiceRegistryManager()
            >>> service = manager.get_service_by_name("apps.CryptoService")
            >>> service['name']
            'apps.CryptoService'
            >>> service['methods']
            ['GetCoin', 'ListCoins', ...]
        """
        services = self.get_all_services()
        return next((s for s in services if s.get("name") == service_name), None)

    def get_service_statistics(
        self, service_name: str, hours: int = 24
    ) -> Dict:
        """
        Get statistics for a specific service (SYNC).

        Args:
            service_name: Service name
            hours: Statistics period in hours (default: 24)

        Returns:
            Dictionary with service statistics

        Example:
            >>> manager = ServiceRegistryManager()
            >>> stats = manager.get_service_statistics("apps.CryptoService", hours=24)
            >>> stats['total']
            150
            >>> stats['successful']
            145
            >>> stats['success_rate']
            96.67
        """
        stats = (
            GRPCRequestLog.objects.filter(service_name=service_name)
            .recent(hours)
            .aggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration=Avg("duration_ms"),
            )
        )

        total = stats["total"] or 0
        successful = stats["successful"] or 0
        success_rate = (successful / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "successful": successful,
            "errors": stats["errors"] or 0,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
        }

    async def aget_service_statistics(
        self, service_name: str, hours: int = 24
    ) -> Dict:
        """
        Get statistics for a specific service (ASYNC - Django 5.2).

        Args:
            service_name: Service name
            hours: Statistics period in hours (default: 24)

        Returns:
            Dictionary with service statistics

        Example:
            >>> manager = ServiceRegistryManager()
            >>> stats = await manager.aget_service_statistics("apps.CryptoService", hours=24)
            >>> stats['total']
            150
            >>> stats['successful']
            145
            >>> stats['success_rate']
            96.67
        """
        # Django 5.2+ async ORM: Use native async aggregate
        stats = await (
            GRPCRequestLog.objects.filter(service_name=service_name)
            .recent(hours)
            .aaggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration=Avg("duration_ms"),
            )
        )

        total = stats["total"] or 0
        successful = stats["successful"] or 0
        success_rate = (successful / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "successful": successful,
            "errors": stats["errors"] or 0,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
        }

    def get_all_services_with_stats(self, hours: int = 24) -> List[Dict]:
        """
        Get all services with their statistics (SYNC).

        Args:
            hours: Statistics period in hours (default: 24)

        Returns:
            List of services with statistics

        Example:
            >>> manager = ServiceRegistryManager()
            >>> services = manager.get_all_services_with_stats(hours=24)
            >>> services[0]['name']
            'apps.CryptoService'
            >>> services[0]['total_requests']
            150
        """
        services = self.get_all_services()
        services_with_stats = []

        for service in services:
            service_name = service.get("name")

            # Get stats from GRPCRequestLog
            stats = (
                GRPCRequestLog.objects.filter(service_name=service_name)
                .recent(hours)
                .aggregate(
                    total=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    avg_duration=Avg("duration_ms"),
                    last_activity=models.Max("created_at"),
                )
            )

            # Calculate success rate
            total = stats["total"] or 0
            successful = stats["successful"] or 0
            success_rate = (successful / total * 100) if total > 0 else 0.0

            # Extract package name
            package = service_name.split(".")[0] if "." in service_name else ""

            # Build dict directly
            service_summary = {
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

            services_with_stats.append(service_summary)

        return services_with_stats

    async def aget_all_services_with_stats(self, hours: int = 24) -> List[Dict]:
        """
        Get all services with their statistics (ASYNC - Django 5.2).

        Args:
            hours: Statistics period in hours (default: 24)

        Returns:
            List of services with statistics

        Example:
            >>> manager = ServiceRegistryManager()
            >>> services = await manager.aget_all_services_with_stats(hours=24)
            >>> services[0]['name']
            'apps.CryptoService'
            >>> services[0]['total_requests']
            150
        """
        # Get all services (sync operation - from cache or filesystem)
        services = self.get_all_services()
        services_with_stats = []

        # Django 5.2+ async ORM: Use native async aggregate
        for service in services:
            service_name = service.get("name")

            # Get stats from GRPCRequestLog using native async aggregate
            stats = await (
                GRPCRequestLog.objects.filter(service_name=service_name)
                .recent(hours)
                .aaggregate(
                    total=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    avg_duration=Avg("duration_ms"),
                    last_activity=models.Max("created_at"),
                )
            )

            # Calculate success rate
            total = stats["total"] or 0
            successful = stats["successful"] or 0
            success_rate = (successful / total * 100) if total > 0 else 0.0

            # Extract package name
            package = service_name.split(".")[0] if "." in service_name else ""

            # Build dict directly
            service_summary = {
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

            services_with_stats.append(service_summary)

        return services_with_stats

    def get_service_methods_with_stats(
        self, service_name: str
    ) -> List[Dict]:
        """
        Get all methods for a service with statistics (SYNC).

        Args:
            service_name: Service name

        Returns:
            List of methods with statistics

        Example:
            >>> manager = ServiceRegistryManager()
            >>> methods = manager.get_service_methods_with_stats("apps.CryptoService")
            >>> methods[0]['name']
            'GetCoin'
            >>> methods[0]['stats']['total_requests']
            50
        """
        service = self.get_service_by_name(service_name)
        if not service:
            return []

        methods_list = []
        for method_name in service.get("methods", []):
            # Get durations for percentile calculation
            durations = list(
                GRPCRequestLog.objects.filter(
                    service_name=service_name,
                    method_name=method_name,
                    duration_ms__isnull=False,
                ).values_list("duration_ms", flat=True)
            )

            # Get aggregate stats
            stats = GRPCRequestLog.objects.filter(
                service_name=service_name,
                method_name=method_name,
            ).aggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration=Avg("duration_ms"),
            )

            # Calculate percentiles
            p50, p95, p99 = self._calculate_percentiles(durations)

            # Calculate success rate
            total = stats["total"] or 0
            successful = stats["successful"] or 0
            success_rate = (successful / total * 100) if total > 0 else 0.0

            # Build method stats dict
            method_stats = {
                "total_requests": total,
                "successful": successful,
                "errors": stats["errors"] or 0,
                "success_rate": round(success_rate, 2),
                "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
                "p50_duration_ms": p50,
                "p95_duration_ms": p95,
                "p99_duration_ms": p99,
            }

            # Build method summary dict
            method_summary = {
                "name": method_name,
                "full_name": f"/{service_name}/{method_name}",
                "service_name": service_name,
                "request_type": "",
                "response_type": "",
                "stats": method_stats,
            }

            methods_list.append(method_summary)

        return methods_list

    async def aget_service_methods_with_stats(
        self, service_name: str
    ) -> List[Dict]:
        """
        Get all methods for a service with statistics (ASYNC - Django 5.2).

        Args:
            service_name: Service name

        Returns:
            List of methods with statistics

        Example:
            >>> manager = ServiceRegistryManager()
            >>> methods = await manager.aget_service_methods_with_stats("apps.CryptoService")
            >>> methods[0]['name']
            'GetCoin'
            >>> methods[0]['stats']['total_requests']
            50
        """
        service = self.get_service_by_name(service_name)
        if not service:
            return []

        # Django 5.2+ async ORM: Use native async operations
        methods_list = []
        for method_name in service.get("methods", []):
            # Get durations for percentile calculation using async list comprehension
            durations = [
                duration async for duration in
                GRPCRequestLog.objects.filter(
                    service_name=service_name,
                    method_name=method_name,
                    duration_ms__isnull=False,
                ).values_list("duration_ms", flat=True)
            ]

            # Get aggregate stats using native async aggregate
            stats = await GRPCRequestLog.objects.filter(
                service_name=service_name,
                method_name=method_name,
            ).aaggregate(
                total=Count("id"),
                successful=Count("id", filter=models.Q(status="success")),
                errors=Count("id", filter=models.Q(status="error")),
                avg_duration=Avg("duration_ms"),
            )

            # Calculate percentiles
            p50, p95, p99 = self._calculate_percentiles(durations)

            # Calculate success rate
            total = stats["total"] or 0
            successful = stats["successful"] or 0
            success_rate = (successful / total * 100) if total > 0 else 0.0

            # Build method stats dict
            method_stats = {
                "total_requests": total,
                "successful": successful,
                "errors": stats["errors"] or 0,
                "success_rate": round(success_rate, 2),
                "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
                "p50_duration_ms": p50,
                "p95_duration_ms": p95,
                "p99_duration_ms": p99,
            }

            # Build method summary dict
            method_summary = {
                "name": method_name,
                "full_name": f"/{service_name}/{method_name}",
                "service_name": service_name,
                "request_type": "",
                "response_type": "",
                "stats": method_stats,
            }

            methods_list.append(method_summary)

        return methods_list

    def _calculate_percentiles(self, values):
        """
        Calculate p50, p95, p99 percentiles.

        Args:
            values: List of numeric values

        Returns:
            Tuple of (p50, p95, p99)
        """
        if not values:
            return 0.0, 0.0, 0.0

        sorted_values = sorted(values)
        n = len(sorted_values)

        p50_idx = int(n * 0.50)
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)

        return (
            float(sorted_values[p50_idx] if p50_idx < n else 0),
            float(sorted_values[p95_idx] if p95_idx < n else 0),
            float(sorted_values[p99_idx] if p99_idx < n else 0),
        )

    def is_server_running(self) -> bool:
        """
        Check if gRPC server is currently running.

        Returns:
            True if server is running, False otherwise

        Example:
            >>> manager = ServiceRegistryManager()
            >>> manager.is_server_running()
            True
        """
        return self.get_current_server() is not None


__all__ = ["ServiceRegistryManager"]
