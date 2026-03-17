"""
django_grpc.services.interceptors.metrics — In-memory gRPC metrics collector.

H-3 fix: MetricsConfig.enabled was always ignored — MetricsCollector was created
unconditionally at import time.  Now:
  - Singleton is lazily created on first call to get_metrics_collector().
  - When metrics.enabled=False, get_metrics_collector() returns NullMetricsCollector
    (same interface, all methods are no-ops) so callers need no changes.

H-5: Optional Prometheus export.
  When MetricsConfig.prometheus_enabled=True and `prometheus_client` is installed,
  get_metrics_collector() returns a PrometheusMetricsCollector that uses standard
  gRPC Prometheus metric names:
    grpc_server_started_total{grpc_service, grpc_method, grpc_type}
    grpc_server_handled_total{grpc_service, grpc_method, grpc_type, grpc_code}
    grpc_server_handling_seconds{grpc_service, grpc_method, grpc_type}
    grpc_server_msg_received_total{grpc_service, grpc_method, grpc_type}
    grpc_server_msg_sent_total{grpc_service, grpc_method, grpc_type}

  The `grpc_type` label is derived from the method name convention: methods with
  "Stream" in the short name are labelled "SERVER_STREAMING"/"CLIENT_STREAMING"/
  "BIDI_STREAMING"; all others are "UNARY".  Callers can pass explicit grpc_type
  via record_request_start(method, grpc_type=...).
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Optional, TypedDict


class MethodStats(TypedDict):
    """Per-method stats returned by MetricsCollector.get_stats(method=...)."""
    requests: int
    errors: int
    in_flight: int
    msg_received: int
    msg_sent: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float


class AggregateStats(TypedDict):
    """Aggregate stats returned by MetricsCollector.get_stats()."""
    total_requests: int
    total_errors: int
    total_in_flight: int
    error_rate: float
    methods: dict[str, MethodStats]


def _get_metrics_config():
    """Read MetricsConfig from grpc_module settings. Returns None on failure."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import settings
        return settings.metrics
    except Exception:
        return None


def _get_response_time_ttl() -> float:
    """Read response_time_ttl from grpc_module config. Falls back to 3600.0."""
    cfg = _get_metrics_config()
    return cfg.response_time_ttl if cfg else 3600.0


def _is_metrics_enabled() -> bool:
    """Read metrics.enabled from config. Defaults to True (backward compatible)."""
    cfg = _get_metrics_config()
    return cfg.enabled if cfg is not None else True


def _is_prometheus_enabled() -> bool:
    """Read metrics.prometheus_enabled from config. Defaults to False."""
    cfg = _get_metrics_config()
    return cfg.prometheus_enabled if cfg is not None else False


class MetricsCollector:
    """Thread-safe (enough for async context) metrics collector for gRPC."""

    def __init__(self, response_time_ttl: float | None = None):
        self.request_counts: dict[str, int] = defaultdict(int)
        self.error_counts: dict[str, int] = defaultdict(int)
        # Stores (duration_ms, timestamp) tuples; old entries pruned in record_response_time()
        self.response_times: dict[str, list[tuple[float, float]]] = defaultdict(list)
        self.total_requests: int = 0
        self.total_errors: int = 0
        self._response_time_ttl: float = response_time_ttl if response_time_ttl is not None else _get_response_time_ttl()
        # G-6: in-flight gauge. Equivalent to grpc_server_started_total - grpc_server_handled_total.
        # Incremented in record_request_start(), decremented in record_request_end().
        self.in_flight_counts: dict[str, int] = defaultdict(int)
        # H-5: message-level counters (grpc_server_msg_received/sent_total)
        self.msg_received_counts: dict[str, int] = defaultdict(int)
        self.msg_sent_counts: dict[str, int] = defaultdict(int)

    def record_request(self, method: str) -> None:
        """Alias for record_request_start (backward-compat)."""
        self.record_request_start(method)

    def record_request_start(self, method: str) -> None:
        # G-6: track in-flight before incrementing totals
        self.in_flight_counts[method] += 1
        self.request_counts[method] += 1
        self.total_requests += 1

    def record_request_end(self, method: str) -> None:
        """G-6: decrement in-flight counter when RPC completes (success or error)."""
        self.in_flight_counts[method] = max(0, self.in_flight_counts[method] - 1)

    def record_messages_received(self, method: str, count: int = 1) -> None:
        """H-5: track inbound message count (grpc_server_msg_received_total)."""
        self.msg_received_counts[method] += count

    def record_messages_sent(self, method: str, count: int = 1) -> None:
        """H-5: track outbound message count (grpc_server_msg_sent_total)."""
        self.msg_sent_counts[method] += count

    def record_error(self, method: str) -> None:
        self.error_counts[method] += 1
        self.total_errors += 1

    def record_response_time(self, method: str, duration_ms: float) -> None:
        now = time.monotonic()
        self.response_times[method].append((duration_ms, now))
        # Prune entries older than TTL to prevent unbounded list growth
        cutoff = now - self._response_time_ttl
        self.response_times[method] = [
            (d, t) for d, t in self.response_times[method] if t >= cutoff
        ]

    def get_stats(self, method: str | None = None) -> MethodStats | AggregateStats:
        if method:
            times = [d for d, _ in self.response_times.get(method, [])]
            return MethodStats(
                requests=self.request_counts.get(method, 0),
                errors=self.error_counts.get(method, 0),
                in_flight=self.in_flight_counts.get(method, 0),
                msg_received=self.msg_received_counts.get(method, 0),
                msg_sent=self.msg_sent_counts.get(method, 0),
                avg_time_ms=sum(times) / len(times) if times else 0.0,
                min_time_ms=min(times) if times else 0.0,
                max_time_ms=max(times) if times else 0.0,
            )
        return AggregateStats(
            total_requests=self.total_requests,
            total_errors=self.total_errors,
            total_in_flight=sum(self.in_flight_counts.values()),
            error_rate=self.total_errors / self.total_requests if self.total_requests > 0 else 0.0,
            methods={m: self.get_stats(m) for m in self.request_counts},  # type: ignore[misc]
        )

    def reset(self) -> None:
        self.request_counts.clear()
        self.error_counts.clear()
        self.response_times.clear()
        self.in_flight_counts.clear()
        self.msg_received_counts.clear()
        self.msg_sent_counts.clear()
        self.total_requests = 0
        self.total_errors = 0


class PrometheusMetricsCollector(MetricsCollector):
    """
    H-5: Prometheus-backed MetricsCollector.

    Uses prometheus_client Counter/Histogram with standard gRPC label names.
    Falls back to in-memory MetricsCollector if prometheus_client is not installed.

    Label set: {grpc_service, grpc_method, grpc_type}
    grpc_type values: UNARY, SERVER_STREAMING, CLIENT_STREAMING, BIDI_STREAMING
    """

    def __init__(self, response_time_ttl: float | None = None) -> None:
        super().__init__(response_time_ttl=response_time_ttl)
        try:
            import prometheus_client  # type: ignore[import-untyped]
            _labels = ["grpc_service", "grpc_method", "grpc_type"]
            self._prom_started = prometheus_client.Counter(
                "grpc_server_started_total",
                "Total number of RPCs started on the server.",
                _labels,
            )
            self._prom_handled = prometheus_client.Counter(
                "grpc_server_handled_total",
                "Total number of RPCs completed on the server.",
                _labels + ["grpc_code"],
            )
            self._prom_handling_seconds = prometheus_client.Histogram(
                "grpc_server_handling_seconds",
                "Histogram of response latency (seconds) of gRPC that had been application-level handled by the server.",
                _labels,
            )
            self._prom_msg_received = prometheus_client.Counter(
                "grpc_server_msg_received_total",
                "Total number of RPC stream messages received on the server.",
                _labels,
            )
            self._prom_msg_sent = prometheus_client.Counter(
                "grpc_server_msg_sent_total",
                "Total number of gRPC stream messages sent by the server.",
                _labels,
            )
            self._prometheus_available = True
        except ImportError:
            self._prometheus_available = False

    def _parse_labels(self, method: str, grpc_type: str = "UNARY") -> tuple[str, str, str]:
        """Return (grpc_service, grpc_method, grpc_type) from a full gRPC method path."""
        from .utils import parse_method
        service, method_name = parse_method(method)
        return service, method_name, grpc_type

    def record_request_start(self, method: str, grpc_type: str = "UNARY") -> None:  # type: ignore[override]
        super().record_request_start(method)
        if self._prometheus_available:
            svc, mth, gtype = self._parse_labels(method, grpc_type)
            self._prom_started.labels(grpc_service=svc, grpc_method=mth, grpc_type=gtype).inc()

    def record_request_end(self, method: str, grpc_code: str = "OK", grpc_type: str = "UNARY") -> None:  # type: ignore[override]
        super().record_request_end(method)
        if self._prometheus_available:
            svc, mth, gtype = self._parse_labels(method, grpc_type)
            self._prom_handled.labels(grpc_service=svc, grpc_method=mth, grpc_type=gtype, grpc_code=grpc_code).inc()

    def record_response_time(self, method: str, duration_ms: float, grpc_type: str = "UNARY") -> None:  # type: ignore[override]
        super().record_response_time(method, duration_ms)
        if self._prometheus_available:
            svc, mth, gtype = self._parse_labels(method, grpc_type)
            self._prom_handling_seconds.labels(grpc_service=svc, grpc_method=mth, grpc_type=gtype).observe(duration_ms / 1000.0)

    def record_messages_received(self, method: str, count: int = 1, grpc_type: str = "UNARY") -> None:  # type: ignore[override]
        super().record_messages_received(method, count)
        if self._prometheus_available:
            svc, mth, gtype = self._parse_labels(method, grpc_type)
            self._prom_msg_received.labels(grpc_service=svc, grpc_method=mth, grpc_type=gtype).inc(count)

    def record_messages_sent(self, method: str, count: int = 1, grpc_type: str = "UNARY") -> None:  # type: ignore[override]
        super().record_messages_sent(method, count)
        if self._prometheus_available:
            svc, mth, gtype = self._parse_labels(method, grpc_type)
            self._prom_msg_sent.labels(grpc_service=svc, grpc_method=mth, grpc_type=gtype).inc(count)


class NullMetricsCollector(MetricsCollector):
    """
    H-3: no-op MetricsCollector returned when metrics.enabled=False.

    All methods are no-ops; get_stats() returns empty dict.
    Callers that hold a reference to MetricsCollector need no code changes.
    """

    def __init__(self) -> None:
        # Deliberately skip parent __init__ — no storage needed
        pass  # type: ignore[misc]

    def record_request(self, method: str) -> None:
        pass

    def record_request_start(self, method: str) -> None:
        pass

    def record_request_end(self, method: str) -> None:
        pass

    def record_messages_received(self, method: str, count: int = 1) -> None:
        pass

    def record_messages_sent(self, method: str, count: int = 1) -> None:
        pass

    def record_error(self, method: str) -> None:
        pass

    def record_response_time(self, method: str, duration_ms: float) -> None:
        pass

    def get_stats(self, method: str | None = None) -> MethodStats | AggregateStats:
        if method:
            return MethodStats(requests=0, errors=0, in_flight=0, msg_received=0, msg_sent=0, avg_time_ms=0.0, min_time_ms=0.0, max_time_ms=0.0)
        return AggregateStats(total_requests=0, total_errors=0, total_in_flight=0, error_rate=0.0, methods={})

    def reset(self) -> None:
        pass


# H-3: lazy singleton — not created at import time.
# Created on first call to get_metrics_collector() so the config is available.
_metrics: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Return the metrics collector singleton.

    H-3: reads metrics.enabled on first call.
    H-5: reads metrics.prometheus_enabled on first call.

    Decision matrix:
    - enabled=False                            → NullMetricsCollector (no-op)
    - enabled=True, prometheus_enabled=False   → MetricsCollector (in-memory)
    - enabled=True, prometheus_enabled=True    → PrometheusMetricsCollector
      (falls back to in-memory if prometheus_client not installed)
    """
    global _metrics
    if _metrics is None:
        if not _is_metrics_enabled():
            _metrics = NullMetricsCollector()
        elif _is_prometheus_enabled():
            _metrics = PrometheusMetricsCollector()
        else:
            _metrics = MetricsCollector()
    return _metrics


def get_metrics(method: str | None = None) -> MethodStats | AggregateStats:
    return get_metrics_collector().get_stats(method)


def reset_metrics() -> None:
    get_metrics_collector().reset()


__all__ = [
    "MetricsCollector",
    "PrometheusMetricsCollector",
    "NullMetricsCollector",
    "get_metrics_collector",
    "get_metrics",
    "reset_metrics",
]
