"""
Monitoring Service.

Provides business logic for gRPC monitoring and statistics.
D1-backed — no ORM, reads from Cloudflare D1 via GrpcD1Service.
"""

from __future__ import annotations

import socket
from datetime import datetime
from typing import Dict, List, Optional

from django_cfg.utils import get_logger

from ...events.service import GrpcD1Service
from ...events.types import GrpcRequestLogRow
from ..discovery import ServiceDiscovery
from ..management.config_helper import get_grpc_server_config

logger = get_logger("grpc.monitoring_service")


def _get_d1() -> GrpcD1Service:
    return GrpcD1Service()


class MonitoringService:
    """
    Service for gRPC monitoring operations.

    Provides methods to retrieve health status, statistics, and monitoring data.
    All data is read from Cloudflare D1 (no ORM).
    """

    def get_health_status(self) -> Dict:
        """
        Get gRPC server health status.

        Returns:
            Dictionary with health status data
        """
        grpc_server_config = get_grpc_server_config()

        if not grpc_server_config:
            raise ValueError("gRPC not configured")

        # Check if server is actually running via D1
        try:
            status_rows = _get_d1().get_server_status()
            current_server = status_rows[0] if status_rows else None
            is_running = bool(current_server and current_server.status == "running")
        except Exception:
            is_running = False

        return {
            "status": "healthy" if is_running else "stopped",
            "server_host": grpc_server_config.host,
            "server_port": grpc_server_config.port,
            "enabled": is_running,
            "timestamp": datetime.now().isoformat(),
        }

    def get_overview_statistics(self, hours: int = 24) -> Dict:
        """
        Get overview statistics for gRPC requests with server information.

        Args:
            hours: Statistics period in hours (1-168)

        Returns:
            Dictionary with overview statistics and server info
        """
        hours = min(max(hours, 1), 168)

        try:
            raw = _get_d1().get_request_stats(hours=hours)
            stats = {
                "total":           raw.get("total", 0),
                "successful":      raw.get("success_count", 0),
                "errors":          raw.get("error_count", 0),
                "avg_duration_ms": raw.get("avg_duration_ms", 0),
            }
        except Exception:
            stats = {"total": 0, "successful": 0, "errors": 0, "avg_duration_ms": 0}

        stats["period_hours"] = hours
        stats["server"] = self._get_server_info_for_overview(hours=hours)
        return stats

    def _get_server_info_for_overview(self, hours: int) -> Dict:
        """Get server information for overview endpoint."""
        grpc_server_config = get_grpc_server_config()
        default_host = grpc_server_config.host if grpc_server_config else "[::]"
        default_port = grpc_server_config.port if grpc_server_config else 50051

        try:
            status_rows = _get_d1().get_server_status()
            current_server = status_rows[0] if status_rows else None
        except Exception:
            current_server = None

        if not current_server:
            return {
                "status": "stopped",
                "is_running": False,
                "host": default_host,
                "port": default_port,
                "address": f"{default_host}:{default_port}",
                "pid": None,
                "hostname": socket.gethostname(),
                "started_at": None,
                "uptime_seconds": 0,
                "last_heartbeat": None,
                "services": [],
            }

        # Get request stats per service
        try:
            recent_logs = _get_d1().get_recent_request_logs(hours=hours, limit=10000)
        except Exception:
            recent_logs = []

        # Aggregate per service
        service_stats_lookup: Dict[str, Dict] = {}
        for row in recent_logs:
            svc = row.service_name
            if svc not in service_stats_lookup:
                service_stats_lookup[svc] = {"total": 0, "errors": 0}
            service_stats_lookup[svc]["total"] += 1
            if row.status == "error":
                service_stats_lookup[svc]["errors"] += 1

        # Get registered services from service discovery
        try:
            discovery = ServiceDiscovery()
            registered_services = discovery.get_registered_services()
        except Exception:
            registered_services = []

        services_list = []
        total_errors = 0

        for service in registered_services:
            service_name = service.get("name", "")
            full_name = service.get("full_name", service_name)
            methods = service.get("methods", [])

            svc_stats = service_stats_lookup.get(full_name, {"total": 0, "errors": 0})
            request_count = svc_stats["total"]
            error_count = svc_stats["errors"]
            success_rate = (
                ((request_count - error_count) / request_count * 100)
                if request_count > 0
                else 100.0
            )
            total_errors += error_count

            services_list.append({
                "name": service_name,
                "full_name": full_name,
                "methods_count": len(methods),
                "request_count": request_count,
                "error_count": error_count,
                "success_rate": round(success_rate, 2),
            })

        services_list.sort(key=lambda x: x["request_count"], reverse=True)

        return {
            "status": current_server.status,
            "is_running": current_server.status == "running",
            "host": current_server.host or default_host,
            "port": current_server.port or default_port,
            "address": current_server.address or f"{default_host}:{default_port}",
            "pid": current_server.pid,
            "hostname": current_server.hostname or socket.gethostname(),
            "started_at": current_server.started_at,
            "uptime_seconds": 0,
            "last_heartbeat": current_server.last_heartbeat,
            "services": services_list,
        }

    def get_recent_requests(
        self,
        service_name: Optional[str] = None,
        method_name: Optional[str] = None,
        status_filter: Optional[str] = None,
        hours: int = 24,
        limit: int = 100,
    ) -> List[GrpcRequestLogRow]:
        """
        Get recent gRPC requests from D1.

        Args:
            service_name: Filter by service name
            method_name: Filter by method name
            status_filter: Filter by status (success/error)
            hours: Time window in hours
            limit: Max records to return

        Returns:
            List of request log rows
        """
        try:
            rows = _get_d1().get_recent_request_logs(
                hours=hours,
                service=service_name,
                limit=limit,
            )
        except Exception:
            rows = []

        # Apply remaining filters
        if method_name:
            rows = [r for r in rows if r.method_name == method_name]
        if status_filter:
            rows = [r for r in rows if r.status == status_filter]

        return rows

    def get_service_statistics(self, hours: int = 24) -> List[Dict]:
        """
        Get statistics per service.

        Args:
            hours: Statistics period in hours

        Returns:
            List of service statistics
        """
        hours = min(max(hours, 1), 168)

        try:
            rows = _get_d1().get_recent_request_logs(hours=hours, limit=50000)
        except Exception:
            return []

        # Aggregate
        agg: Dict[str, Dict] = {}
        for row in rows:
            svc = row.service_name
            if svc not in agg:
                agg[svc] = {"total": 0, "successful": 0, "errors": 0, "durations": [], "last_activity_at": None}
            agg[svc]["total"] += 1
            if row.status == "success":
                agg[svc]["successful"] += 1
            elif row.status == "error":
                agg[svc]["errors"] += 1
            if row.duration_ms is not None:
                agg[svc]["durations"].append(row.duration_ms)
            ts = row.created_at
            if ts and (not agg[svc]["last_activity_at"] or ts > agg[svc]["last_activity_at"]):
                agg[svc]["last_activity_at"] = ts

        result = []
        for svc_name, data in sorted(agg.items(), key=lambda x: -x[1]["total"]):
            durations = data["durations"]
            avg_dur = sum(durations) / len(durations) if durations else 0
            result.append({
                "service_name": svc_name,
                "total": data["total"],
                "successful": data["successful"],
                "errors": data["errors"],
                "avg_duration_ms": round(avg_dur, 2),
                "last_activity_at": data["last_activity_at"],
            })

        return result

    def get_method_statistics(
        self, service_name: Optional[str] = None, hours: int = 24
    ) -> List[Dict]:
        """
        Get statistics per method.

        Args:
            service_name: Filter by service name
            hours: Statistics period in hours

        Returns:
            List of method statistics
        """
        hours = min(max(hours, 1), 168)

        try:
            rows = _get_d1().get_recent_request_logs(
                hours=hours,
                service=service_name,
                limit=50000,
            )
        except Exception:
            return []

        # Aggregate per (service_name, method_name)
        agg: Dict[tuple, Dict] = {}
        for row in rows:
            key = (row.service_name, row.method_name)
            if key not in agg:
                agg[key] = {"total": 0, "successful": 0, "errors": 0, "durations": [], "last_activity_at": None}
            agg[key]["total"] += 1
            if row.status == "success":
                agg[key]["successful"] += 1
            elif row.status == "error":
                agg[key]["errors"] += 1
            if row.duration_ms is not None:
                agg[key]["durations"].append(row.duration_ms)
            ts = row.created_at
            if ts and (not agg[key]["last_activity_at"] or ts > agg[key]["last_activity_at"]):
                agg[key]["last_activity_at"] = ts

        result = []
        for (svc, method), data in sorted(agg.items(), key=lambda x: -x[1]["total"]):
            durations = data["durations"]
            avg_dur = sum(durations) / len(durations) if durations else 0
            result.append({
                "service_name": svc,
                "method_name": method,
                "total": data["total"],
                "successful": data["successful"],
                "errors": data["errors"],
                "avg_duration_ms": round(avg_dur, 2),
                "last_activity_at": data["last_activity_at"],
            })

        return result

    def get_timeline_data(self, hours: int = 24, granularity: str = "hour") -> List[Dict]:
        """
        Get timeline data for requests.

        Args:
            hours: Period in hours
            granularity: 'hour' or 'day'

        Returns:
            List of timeline data points
        """
        hours = min(max(hours, 1), 168)

        try:
            rows = _get_d1().get_recent_request_logs(hours=hours, limit=50000)
        except Exception:
            return []

        use_day = granularity == "day" or hours > 48
        time_fmt = "%Y-%m-%d" if use_day else "%Y-%m-%d %H:00"

        # Bucket rows by truncated timestamp
        buckets: Dict[str, Dict] = {}
        for row in rows:
            ts_str = row.created_at
            if not ts_str:
                continue
            try:
                if isinstance(ts_str, str):
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                else:
                    ts = ts_str
                if use_day:
                    bucket_key = ts.strftime("%Y-%m-%d")
                else:
                    bucket_key = ts.strftime("%Y-%m-%d %H:00")
            except Exception:
                continue

            if bucket_key not in buckets:
                buckets[bucket_key] = {"total": 0, "successful": 0, "errors": 0, "durations": []}
            buckets[bucket_key]["total"] += 1
            if row.status == "success":
                buckets[bucket_key]["successful"] += 1
            elif row.status == "error":
                buckets[bucket_key]["errors"] += 1
            if row.duration_ms is not None:
                buckets[bucket_key]["durations"].append(row.duration_ms)

        result = []
        for ts_key in sorted(buckets):
            data = buckets[ts_key]
            durations = data["durations"]
            avg_dur = sum(durations) / len(durations) if durations else 0
            result.append({
                "timestamp": ts_key,
                "total": data["total"],
                "successful": data["successful"],
                "errors": data["errors"],
                "avg_duration_ms": round(avg_dur, 2),
            })

        return result


__all__ = ["MonitoringService"]
