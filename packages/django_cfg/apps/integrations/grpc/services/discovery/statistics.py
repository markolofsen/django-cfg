"""
Statistics calculations for gRPC services.
"""

from typing import Dict, List, Tuple

from django.db import models
from django.db.models import Avg, Count

from ...models import GRPCRequestLog


def calculate_percentiles(values: List[float]) -> Tuple[float, float, float]:
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


def get_service_statistics(service_name: str, hours: int = 24) -> Dict:
    """
    Get statistics for a specific service (SYNC).

    Args:
        service_name: Service name
        hours: Statistics period in hours (default: 24)

    Returns:
        Dictionary with service statistics
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


async def aget_service_statistics(service_name: str, hours: int = 24) -> Dict:
    """
    Get statistics for a specific service (ASYNC - Django 5.2).

    Args:
        service_name: Service name
        hours: Statistics period in hours (default: 24)

    Returns:
        Dictionary with service statistics
    """
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


def get_method_statistics(service_name: str, method_name: str) -> Dict:
    """
    Get statistics for a specific method (SYNC).

    Args:
        service_name: Service name
        method_name: Method name

    Returns:
        Dictionary with method statistics
    """
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

    p50, p95, p99 = calculate_percentiles(durations)

    total = stats["total"] or 0
    successful = stats["successful"] or 0
    success_rate = (successful / total * 100) if total > 0 else 0.0

    return {
        "total_requests": total,
        "successful": successful,
        "errors": stats["errors"] or 0,
        "success_rate": round(success_rate, 2),
        "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
        "p50_duration_ms": p50,
        "p95_duration_ms": p95,
        "p99_duration_ms": p99,
    }


async def aget_method_statistics(service_name: str, method_name: str) -> Dict:
    """
    Get statistics for a specific method (ASYNC - Django 5.2).

    Args:
        service_name: Service name
        method_name: Method name

    Returns:
        Dictionary with method statistics
    """
    # Get durations using async iteration
    durations = [
        duration async for duration in
        GRPCRequestLog.objects.filter(
            service_name=service_name,
            method_name=method_name,
            duration_ms__isnull=False,
        ).values_list("duration_ms", flat=True)
    ]

    # Get aggregate stats
    stats = await GRPCRequestLog.objects.filter(
        service_name=service_name,
        method_name=method_name,
    ).aaggregate(
        total=Count("id"),
        successful=Count("id", filter=models.Q(status="success")),
        errors=Count("id", filter=models.Q(status="error")),
        avg_duration=Avg("duration_ms"),
    )

    p50, p95, p99 = calculate_percentiles(durations)

    total = stats["total"] or 0
    successful = stats["successful"] or 0
    success_rate = (successful / total * 100) if total > 0 else 0.0

    return {
        "total_requests": total,
        "successful": successful,
        "errors": stats["errors"] or 0,
        "success_rate": round(success_rate, 2),
        "avg_duration_ms": round(stats["avg_duration"] or 0, 2),
        "p50_duration_ms": p50,
        "p95_duration_ms": p95,
        "p99_duration_ms": p99,
    }


__all__ = [
    "calculate_percentiles",
    "get_service_statistics",
    "aget_service_statistics",
    "get_method_statistics",
    "aget_method_statistics",
]
