"""Dashboard service for Streamlit admin.

Provides dashboard data: statistics, health, metrics, actions.
"""

from datetime import datetime

from models.dashboard import (
    ChangeType,
    ComponentHealth,
    HealthStatus,
    MetricPoint,
    QuickAction,
    StatCard,
    SystemHealth,
    SystemMetrics,
)
from services.base import BaseService


class DashboardService(BaseService):
    """Dashboard data service."""

    def get_stat_cards(self) -> list[StatCard]:
        """Fetch dashboard statistics - return mock data for now."""
        # Return mock data to avoid API timeout issues during development
        return [
            StatCard(title="RQ Jobs", value="42", icon="list", change="+5 today", change_type=ChangeType.UP),
            StatCard(title="Workers", value="3", icon="cpu", change_type=ChangeType.UP),
            StatCard(title="Centrifugo", value="Healthy", icon="radio", change_type=ChangeType.UP),
            StatCard(title="gRPC Services", value="5", icon="server"),
        ]

    def _get_rq_stats(self) -> StatCard:
        """Get RQ queue statistics."""
        default = StatCard(title="RQ Jobs", value="—", icon="list")

        def fetch() -> StatCard:
            queues = self.api.cfg_rq_queues.list()
            total_jobs = sum(q.count for q in queues)
            failed_jobs = sum(q.failed_jobs or 0 for q in queues)
            return StatCard(
                title="RQ Jobs",
                value=str(total_jobs),
                icon="list",
                change=f"{failed_jobs} failed" if failed_jobs else None,
                change_type=ChangeType.DOWN if failed_jobs else ChangeType.NEUTRAL,
            )

        return self._safe_call("rq_stats", fetch, default)

    def _get_workers_stats(self) -> StatCard:
        """Get RQ workers statistics."""
        default = StatCard(title="Workers", value="—", icon="cpu")

        def fetch() -> StatCard:
            workers = self.api.cfg_rq_workers.list()
            worker_count = len(workers)
            return StatCard(
                title="Workers",
                value=str(worker_count),
                icon="cpu",
                change_type=ChangeType.UP if worker_count > 0 else ChangeType.DOWN,
            )

        return self._safe_call("workers_stats", fetch, default)

    def _get_centrifugo_stats(self) -> StatCard:
        """Get Centrifugo statistics."""
        default = StatCard(title="WS Clients", value="—", icon="radio")

        def fetch() -> StatCard:
            health = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_health_retrieve()
            # CentrifugoHealthCheck has status: str ("healthy"/"unhealthy")
            is_healthy = health.status == "healthy"
            return StatCard(
                title="Centrifugo",
                value="Healthy" if is_healthy else "Unhealthy",
                icon="radio",
                change_type=ChangeType.UP if is_healthy else ChangeType.DOWN,
            )

        return self._safe_call("centrifugo_stats", fetch, default)

    def _get_grpc_stats(self) -> StatCard:
        """Get gRPC services statistics."""
        default = StatCard(title="gRPC Services", value="—", icon="server")

        def fetch() -> StatCard:
            # list() returns PaginatedServiceSummaryList with .count
            paginated = self.api.cfg_grpc_services.list()
            service_count = paginated.count
            return StatCard(
                title="gRPC Services",
                value=str(service_count),
                icon="server",
            )

        return self._safe_call("grpc_stats", fetch, default)

    def get_system_health(self) -> SystemHealth:
        """Return mock system health data."""
        return SystemHealth(
            percentage=100,
            status=HealthStatus.HEALTHY,
            components=[
                ComponentHealth(name="Redis Queue", status=HealthStatus.HEALTHY, message="3 workers active"),
                ComponentHealth(name="Centrifugo", status=HealthStatus.HEALTHY, message="WebSocket server healthy"),
            ],
            updated_at=datetime.now(),
        )

    def _check_rq_health(self) -> ComponentHealth:
        """Check RQ workers health."""
        default = ComponentHealth(
            name="Redis Queue",
            status=HealthStatus.ERROR,
            message="Connection failed",
        )

        def check() -> ComponentHealth:
            workers = self.api.cfg_rq_workers.list()
            if workers and len(workers) > 0:
                return ComponentHealth(
                    name="Redis Queue",
                    status=HealthStatus.HEALTHY,
                    message=f"{len(workers)} workers active",
                )
            return ComponentHealth(
                name="Redis Queue",
                status=HealthStatus.WARNING,
                message="No active workers",
            )

        return self._safe_call("check_rq", check, default)

    def _check_centrifugo_health(self) -> ComponentHealth:
        """Check Centrifugo health."""
        default = ComponentHealth(
            name="Centrifugo",
            status=HealthStatus.ERROR,
            message="Connection failed",
        )

        def check() -> ComponentHealth:
            health = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_health_retrieve()
            if health.status == "healthy":
                return ComponentHealth(
                    name="Centrifugo",
                    status=HealthStatus.HEALTHY,
                    message="WebSocket server healthy",
                )
            return ComponentHealth(
                name="Centrifugo",
                status=HealthStatus.WARNING,
                message="Degraded",
            )

        return self._safe_call("check_centrifugo", check, default)

    def get_system_metrics(self) -> SystemMetrics:
        """Return mock system metrics data."""
        from datetime import timedelta

        # Generate mock timeline data
        now = datetime.now()
        timeline = [
            MetricPoint(
                timestamp=(now - timedelta(hours=i)).isoformat(),
                count=100 + i * 5,
                successful=95 + i * 4,
                failed=5 + i,
            )
            for i in range(24, 0, -1)
        ]

        return SystemMetrics(
            rq_total=150,
            centrifugo_total=1234,
            centrifugo_success_rate=98.5,
            centrifugo_timeline=timeline,
            grpc_total=567,
            grpc_success_rate=99.2,
        )

    def get_quick_actions(self) -> list[QuickAction]:
        """Get configured quick actions."""
        return [
            QuickAction(label="Clear Cache", icon="trash", action="clear_cache"),
            QuickAction(label="Restart Workers", icon="refresh-cw", action="restart"),
            QuickAction(label="View Logs", icon="file-text", url="/logs"),
            QuickAction(label="System Info", icon="info", url="/system"),
        ]
