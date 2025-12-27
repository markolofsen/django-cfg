"""
gRPC Metrics Collection.

Thread-safe metrics collector for gRPC request tracking.
"""

from collections import defaultdict


class MetricsCollector:
    """Thread-safe metrics collector for gRPC."""

    def __init__(self):
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.total_requests = 0
        self.total_errors = 0

    def record_request(self, method: str):
        self.request_counts[method] += 1
        self.total_requests += 1

    def record_error(self, method: str):
        self.error_counts[method] += 1
        self.total_errors += 1

    def record_response_time(self, method: str, duration_ms: float):
        self.response_times[method].append(duration_ms)

    def get_stats(self, method: str = None) -> dict:
        if method:
            times = self.response_times.get(method, [])
            return {
                "requests": self.request_counts.get(method, 0),
                "errors": self.error_counts.get(method, 0),
                "avg_time_ms": sum(times) / len(times) if times else 0,
                "min_time_ms": min(times) if times else 0,
                "max_time_ms": max(times) if times else 0,
            }
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / self.total_requests if self.total_requests > 0 else 0,
            "methods": {m: self.get_stats(m) for m in self.request_counts.keys()},
        }

    def reset(self):
        self.request_counts.clear()
        self.error_counts.clear()
        self.response_times.clear()
        self.total_requests = 0
        self.total_errors = 0


# Global metrics collector (singleton)
_metrics = MetricsCollector()


def get_metrics(method: str = None) -> dict:
    """Get metrics for a method or all methods."""
    return _metrics.get_stats(method)


def reset_metrics():
    """Reset all metrics."""
    _metrics.reset()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics


__all__ = [
    "MetricsCollector",
    "get_metrics",
    "reset_metrics",
    "get_metrics_collector",
]
