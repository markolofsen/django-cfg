"""System service for Streamlit admin.

Provides system health and configuration monitoring.
"""

from datetime import datetime

from models.dashboard import (
    ChangeType,
    ComponentHealth,
    HealthStatus,
    StatCard,
    SystemHealth,
    SystemMetrics,
)
from services.base import BaseService


class SystemService(BaseService):
    """System monitoring service."""

    def get_overview_stats(self) -> list[StatCard]:
        """Get system overview statistics."""
        stats = []
        stats.append(self._get_rq_stats())
        stats.append(self._get_workers_stats())
        stats.append(self._get_centrifugo_stats())
        stats.append(self._get_grpc_stats())
        return stats

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
        default = StatCard(title="Centrifugo", value="—", icon="radio")

        def fetch() -> StatCard:
            health = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_health_retrieve()
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
            paginated = self.api.cfg_grpc_services.list()
            service_count = paginated.count
            return StatCard(
                title="gRPC Services",
                value=str(service_count),
                icon="server",
            )

        return self._safe_call("grpc_stats", fetch, default)

    def get_system_health(self) -> SystemHealth:
        """Get aggregated system health."""
        components: list[ComponentHealth] = []
        healthy_count = 0
        total_count = 0

        # Check RQ
        total_count += 1
        rq_health = self._check_rq_health()
        components.append(rq_health)
        if rq_health.status == HealthStatus.HEALTHY:
            healthy_count += 1

        # Check Centrifugo
        total_count += 1
        centrifugo_health = self._check_centrifugo_health()
        components.append(centrifugo_health)
        if centrifugo_health.status == HealthStatus.HEALTHY:
            healthy_count += 1

        # Check gRPC
        total_count += 1
        grpc_health = self._check_grpc_health()
        components.append(grpc_health)
        if grpc_health.status == HealthStatus.HEALTHY:
            healthy_count += 1

        # Calculate overall health
        percentage = int((healthy_count / total_count) * 100) if total_count > 0 else 0
        if percentage >= 80:
            status = HealthStatus.HEALTHY
        elif percentage >= 50:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.ERROR

        return SystemHealth(
            percentage=percentage,
            status=status,
            components=components,
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
                message="Degraded performance",
            )

        return self._safe_call("check_centrifugo", check, default)

    def _check_grpc_health(self) -> ComponentHealth:
        """Check gRPC health."""
        default = ComponentHealth(
            name="gRPC",
            status=HealthStatus.ERROR,
            message="Connection failed",
        )

        def check() -> ComponentHealth:
            health = self.api.cfg_grpc_monitoring.grpc_monitor_health_retrieve()
            if health.status == "healthy":
                return ComponentHealth(
                    name="gRPC",
                    status=HealthStatus.HEALTHY,
                    message="gRPC server healthy",
                )
            return ComponentHealth(
                name="gRPC",
                status=HealthStatus.WARNING,
                message="Server degraded",
            )

        return self._safe_call("check_grpc", check, default)

    def get_metrics(self) -> SystemMetrics:
        """Get system metrics from monitoring APIs."""
        return SystemMetrics()
