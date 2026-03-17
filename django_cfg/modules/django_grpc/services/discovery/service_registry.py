"""
Service Registry Manager.

Provides business logic for accessing and managing registered gRPC services.
D1-backed — no ORM.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from django_cfg.utils import get_logger

from .statistics import (
    calculate_percentiles,
    get_service_statistics,
    aget_service_statistics,
    get_method_statistics,
    aget_method_statistics,
)

logger = get_logger("grpc.service_registry")


def _get_d1() -> Any:
    from django_cfg.modules.django_grpc.events.service import GrpcD1Service
    return GrpcD1Service()


class ServiceRegistryManager:
    """
    Manager for accessing registered gRPC services.

    Reads server status from D1 (no ORM).
    """

    def get_current_server(self) -> Optional[Dict]:
        """Get the currently running gRPC server (SYNC). Returns dict or None."""
        try:
            rows = _get_d1().get_server_status()
            if rows:
                row = rows[0]
                if row.status == "running":
                    return row.model_dump()
            return None
        except Exception as e:
            logger.error(f"Error getting current server: {e}", exc_info=True)
            return None

    async def aget_current_server(self) -> Optional[Dict]:
        """Get the currently running gRPC server (ASYNC)."""
        return self.get_current_server()

    def get_all_services(self) -> List[Dict]:
        """Get all registered services."""
        from .service_discovery import ServiceDiscovery
        return ServiceDiscovery().get_registered_services()

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
        result = []
        for service in services:
            service_name = service.get("name") or ""
            stats = self._get_service_summary_stats(service_name, hours)
            result.append(self._build_service_summary(service, service_name, stats))
        return result

    async def aget_all_services_with_stats(self, hours: int = 24) -> List[Dict]:
        """Get all services with their statistics (ASYNC)."""
        services = self.get_all_services()
        result = []
        for service in services:
            service_name = service.get("name") or ""
            stats = await self._aget_service_summary_stats(service_name, hours)
            result.append(self._build_service_summary(service, service_name, stats))
        return result

    def get_service_methods_with_stats(self, service_name: str) -> List[Dict]:
        """Get all methods for a service with statistics (SYNC)."""
        service = self.get_service_by_name(service_name)
        if not service:
            return []
        result = []
        for method_name in service.get("methods", []):
            method_stats = get_method_statistics(service_name, method_name)
            result.append(self._build_method_summary(service_name, method_name, method_stats))
        return result

    async def aget_service_methods_with_stats(self, service_name: str) -> List[Dict]:
        """Get all methods for a service with statistics (ASYNC)."""
        service = self.get_service_by_name(service_name)
        if not service:
            return []
        result = []
        for method_name in service.get("methods", []):
            method_stats = await aget_method_statistics(service_name, method_name)
            result.append(self._build_method_summary(service_name, method_name, method_stats))
        return result

    def is_server_running(self) -> bool:
        """Check if gRPC server is currently running."""
        return self.get_current_server() is not None

    # Helpers

    def _get_service_summary_stats(self, service_name: str, hours: int) -> Dict:
        return get_service_statistics(service_name, hours)

    async def _aget_service_summary_stats(self, service_name: str, hours: int) -> Dict:
        return await aget_service_statistics(service_name, hours)

    def _build_service_summary(self, service: Dict, service_name: Optional[str], stats: Dict) -> Dict:
        name = service_name or ""
        total = stats.get("total", 0)
        successful = stats.get("successful", 0)
        success_rate = (successful / total * 100) if total > 0 else 0.0
        package = name.split(".")[0] if "." in name else ""
        return {
            "name": name,
            "full_name": service.get("full_name", f"/{name}"),
            "package": package,
            "methods_count": len(service.get("methods", [])),
            "total_requests": total,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(stats.get("avg_duration_ms", 0), 2),
            "last_activity_at": stats.get("last_activity_at"),
        }

    def _build_method_summary(self, service_name: str, method_name: str, stats: Dict) -> Dict:
        return {
            "name": method_name,
            "full_name": f"/{service_name}/{method_name}",
            "service_name": service_name,
            "request_type": "",
            "response_type": "",
            "stats": stats,
        }


__all__ = ["ServiceRegistryManager"]
