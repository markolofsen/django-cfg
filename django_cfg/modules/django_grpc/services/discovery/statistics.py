"""
Statistics calculations for gRPC services.
D1-backed — no ORM.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def _get_d1() -> Any:
    from django_cfg.modules.django_grpc.events.service import GrpcD1Service
    return GrpcD1Service()


def calculate_percentiles(values: List[float]) -> Tuple[float, float, float]:
    """Calculate p50, p95, p99 percentiles."""
    if not values:
        return 0.0, 0.0, 0.0
    sv = sorted(values)
    n = len(sv)
    return (
        float(sv[min(int(n * 0.50), n - 1)]),
        float(sv[min(int(n * 0.95), n - 1)]),
        float(sv[min(int(n * 0.99), n - 1)]),
    )


def _aggregate_from_rows(rows: list) -> Dict:
    total = len(rows)
    successful = sum(1 for r in rows if r.status == "success")
    errors = sum(1 for r in rows if r.status == "error")
    durations = [r.duration_ms for r in rows if r.duration_ms is not None]
    avg_dur = sum(durations) / len(durations) if durations else 0
    return {"total": total, "successful": successful, "errors": errors,
            "avg_duration": avg_dur, "durations": durations}


def get_service_statistics(service_name: str, hours: int = 24) -> Dict:
    """Get statistics for a specific service (SYNC)."""
    try:
        rows = _get_d1().get_recent_request_logs(hours=hours, service=service_name, limit=50000)
    except Exception:
        rows = []
    data = _aggregate_from_rows(rows)
    total = data["total"]
    successful = data["successful"]
    return {
        "total": total,
        "successful": successful,
        "errors": data["errors"],
        "success_rate": round((successful / total * 100) if total > 0 else 0.0, 2),
        "avg_duration_ms": round(data["avg_duration"], 2),
    }


async def aget_service_statistics(service_name: str, hours: int = 24) -> Dict:
    """Get statistics for a specific service (ASYNC)."""
    return get_service_statistics(service_name, hours)


def get_method_statistics(service_name: str, method_name: str, hours: int = 24) -> Dict:
    """Get statistics for a specific method (SYNC)."""
    try:
        rows = _get_d1().get_recent_request_logs(hours=hours, service=service_name, limit=50000)
    except Exception:
        rows = []
    rows = [r for r in rows if r.method_name == method_name]
    data = _aggregate_from_rows(rows)
    p50, p95, p99 = calculate_percentiles(data["durations"])
    total = data["total"]
    successful = data["successful"]
    return {
        "total_requests": total,
        "successful": successful,
        "errors": data["errors"],
        "success_rate": round((successful / total * 100) if total > 0 else 0.0, 2),
        "avg_duration_ms": round(data["avg_duration"], 2),
        "p50_duration_ms": p50,
        "p95_duration_ms": p95,
        "p99_duration_ms": p99,
    }


async def aget_method_statistics(service_name: str, method_name: str, hours: int = 24) -> Dict:
    """Get statistics for a specific method (ASYNC)."""
    return get_method_statistics(service_name, method_name, hours)


__all__ = [
    "calculate_percentiles",
    "get_service_statistics",
    "aget_service_statistics",
    "get_method_statistics",
    "aget_method_statistics",
]
