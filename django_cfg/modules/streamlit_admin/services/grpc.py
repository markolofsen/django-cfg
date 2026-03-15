"""gRPC service for Streamlit admin.

Provides gRPC service monitoring and management.
"""

from models.grpc import GRPCHealth, MethodStats, ServiceInfo
from services.base import BaseService


class GRPCService(BaseService):
    """gRPC services management."""

    def get_health(self) -> GRPCHealth:
        """Get gRPC system health."""
        default = GRPCHealth(
            status="error",
            services_count=0,
            methods_count=0,
            total_calls=0,
            error_rate=0.0,
        )

        def fetch() -> GRPCHealth:
            # GRPCHealthCheck has status: str ("healthy"/"unhealthy")
            data = self.api.cfg_grpc_monitoring.grpc_monitor_health_retrieve()
            # For counts, need overview stats
            overview = self.api.cfg_grpc_monitoring.grpc_monitor_overview_retrieve()
            return GRPCHealth(
                status=data.status,
                services_count=len(overview.server.services),
                methods_count=sum(s.methods_count for s in overview.server.services),
                total_calls=overview.total,
                error_rate=100.0 - overview.success_rate,
            )

        return self._safe_call("get_health", fetch, default)

    def get_services(self) -> list[ServiceInfo]:
        """Get all registered gRPC services."""

        def fetch() -> list[ServiceInfo]:
            # PaginatedServiceSummaryList has .results with ServiceSummary items
            paginated = self.api.cfg_grpc_services.list()
            return [
                ServiceInfo(
                    name=s.name,
                    package=s.package,
                    methods_count=s.methods_count,
                    total_calls=s.total_requests or 0,
                    error_count=0,  # Not in ServiceSummary
                    avg_latency_ms=s.avg_duration_ms or 0.0,
                    status="active" if s.last_activity_at else "idle",
                )
                for s in paginated.results
            ]

        return self._safe_call("get_services", fetch, [])

    def get_service_detail(self, service_name: str) -> ServiceInfo | None:
        """Get details for a specific service."""

        def fetch() -> ServiceInfo | None:
            # retrieve() requires both id and pk (same value)
            data = self.api.cfg_grpc_services.retrieve(id=service_name, pk=service_name)
            return ServiceInfo(
                name=data.name,
                package=data.package,
                methods_count=len(data.methods) if data.methods else 0,
                total_calls=data.stats.total_requests or 0,
                error_count=data.stats.errors or 0,
                avg_latency_ms=data.stats.avg_duration_ms or 0.0,
                status="active",
            )

        return self._safe_call("get_service_detail", fetch, None)

    def get_method_stats(self, service_name: str) -> list[MethodStats]:
        """Get method statistics for a service."""

        def fetch() -> list[MethodStats]:
            # MethodList has .methods with MethodSummary items
            data = self.api.cfg_grpc_monitoring.grpc_monitor_methods_retrieve(
                service=service_name
            )
            return [
                MethodStats(
                    name=m.name,
                    calls=m.stats.total_requests or 0,
                    errors=m.stats.errors or 0,
                    avg_latency_ms=m.stats.avg_duration_ms or 0.0,
                    p99_latency_ms=m.stats.p99_duration_ms or 0.0,
                )
                for m in (data.methods or [])
            ]

        return self._safe_call("get_method_stats", fetch, [])

    def get_recent_errors(self, limit: int = 20) -> list[dict]:
        """Get recent gRPC errors."""

        def fetch() -> list[dict]:
            # PaginatedRecentRequestList has .results with RecentRequest items
            paginated = self.api.cfg_grpc_monitoring.grpc_monitor_requests_list(
                status="error",
                page_size=limit,
            )
            return [
                {
                    "service": e.service_name,
                    "method": e.method_name,
                    "code": e.grpc_status_code or "",
                    "message": e.error_message or "",
                    "timestamp": e.created_at,
                }
                for e in paginated.results
            ]

        return self._safe_call("get_recent_errors", fetch, [])

    def get_overview_stats(self) -> dict:
        """Get overview statistics."""

        def fetch() -> dict:
            data = self.api.cfg_grpc_monitoring.grpc_monitor_overview_retrieve()
            return {
                "total": data.total,
                "successful": data.successful,
                "errors": data.errors,
                "cancelled": data.cancelled,
                "timeout": data.timeout,
                "success_rate": data.success_rate,
                "avg_duration_ms": data.avg_duration_ms,
                "p95_duration_ms": data.p95_duration_ms or 0.0,
                "period_hours": data.period_hours,
                "server_status": data.server.status,
                "server_uptime": data.server.uptime_seconds,
            }

        return self._safe_call(
            "get_overview_stats",
            fetch,
            {
                "total": 0,
                "successful": 0,
                "errors": 0,
                "cancelled": 0,
                "timeout": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "p95_duration_ms": 0.0,
                "period_hours": 24,
                "server_status": "unknown",
                "server_uptime": 0,
            },
        )
