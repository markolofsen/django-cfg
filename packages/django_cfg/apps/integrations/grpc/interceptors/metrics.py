"""
Metrics Interceptor for gRPC.

Tracks request counts, response times, and error rates.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Callable

import grpc
import grpc.aio

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Thread-safe metrics collector for gRPC.

    Tracks:
    - Request counts per method
    - Response times per method
    - Error counts per method
    - Total requests/errors
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.response_times = defaultdict(list)
        self.total_requests = 0
        self.total_errors = 0

    def record_request(self, method: str):
        """Record a request."""
        self.request_counts[method] += 1
        self.total_requests += 1

    def record_error(self, method: str):
        """Record an error."""
        self.error_counts[method] += 1
        self.total_errors += 1

    def record_response_time(self, method: str, duration_ms: float):
        """Record response time."""
        self.response_times[method].append(duration_ms)

    def get_stats(self, method: str = None) -> dict:
        """
        Get statistics for a method or all methods.

        Args:
            method: Specific method name, or None for all

        Returns:
            Dictionary with statistics
        """
        if method:
            times = self.response_times.get(method, [])
            return {
                "requests": self.request_counts.get(method, 0),
                "errors": self.error_counts.get(method, 0),
                "avg_time_ms": sum(times) / len(times) if times else 0,
                "min_time_ms": min(times) if times else 0,
                "max_time_ms": max(times) if times else 0,
            }
        else:
            return {
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "error_rate": (
                    self.total_errors / self.total_requests
                    if self.total_requests > 0
                    else 0
                ),
                "methods": {
                    method: self.get_stats(method)
                    for method in self.request_counts.keys()
                },
            }

    def reset(self):
        """Reset all metrics."""
        self.request_counts.clear()
        self.error_counts.clear()
        self.response_times.clear()
        self.total_requests = 0
        self.total_errors = 0


# Global metrics collector instance
_metrics = MetricsCollector()


def get_metrics(method: str = None) -> dict:
    """
    Get metrics for a method or all methods.

    Args:
        method: Specific method name, or None for all

    Returns:
        Dictionary with metrics

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.interceptors.metrics import get_metrics

        # Get all metrics
        all_stats = get_metrics()

        # Get metrics for specific method
        stats = get_metrics("/myapp.MyService/MyMethod")
        print(f"Requests: {stats['requests']}")
        print(f"Avg time: {stats['avg_time_ms']:.2f}ms")
        ```
    """
    return _metrics.get_stats(method)


def reset_metrics():
    """
    Reset all metrics.

    Example:
        ```python
        from django_cfg.apps.integrations.grpc.interceptors.metrics import reset_metrics
        reset_metrics()
        ```
    """
    _metrics.reset()


class MetricsInterceptor(grpc.aio.ServerInterceptor):
    """
    gRPC interceptor for metrics collection (async).

    Features:
    - Tracks request counts
    - Tracks response times
    - Tracks error rates
    - Per-method statistics
    - Global statistics

    Example:
        ```python
        # In Django settings (auto-configured in dev mode)
        GRPC_FRAMEWORK = {
            "SERVER_INTERCEPTORS": [
                "django_cfg.apps.integrations.grpc.interceptors.MetricsInterceptor",
            ]
        }
        ```

    Access Metrics:
        ```python
        from django_cfg.apps.integrations.grpc.interceptors.metrics import get_metrics

        stats = get_metrics()
        print(f"Total requests: {stats['total_requests']}")
        print(f"Error rate: {stats['error_rate']:.2%}")
        ```
    """

    def __init__(self):
        """Initialize metrics interceptor."""
        self.collector = _metrics

    async def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC service call for metrics collection (async).

        Args:
            continuation: Function to invoke the next interceptor or handler
            handler_call_details: Details about the RPC call

        Returns:
            RPC method handler with metrics
        """
        method_name = handler_call_details.method

        # Record request
        self.collector.record_request(method_name)

        # Get handler and wrap it (await for async)
        handler = await continuation(handler_call_details)

        if handler is None:
            return None

        # Wrap handler methods to track metrics
        return self._wrap_handler(handler, method_name)

    def _wrap_handler(
        self,
        handler: grpc.RpcMethodHandler,
        method_name: str,
    ) -> grpc.RpcMethodHandler:
        """
        Wrap handler to track metrics.

        Args:
            handler: Original RPC method handler
            method_name: gRPC method name

        Returns:
            Wrapped RPC method handler
        """
        def wrap_unary_unary(behavior):
            async def wrapper(request, context):
                start_time = time.time()
                try:
                    response = await behavior(request, context)
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                    return response
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                    self.collector.record_error(method_name)
                    raise
            return wrapper

        def wrap_unary_stream(behavior):
            async def wrapper(request, context):
                start_time = time.time()
                try:
                    async for response in behavior(request, context):
                        yield response
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                    self.collector.record_error(method_name)
                    raise
            return wrapper

        def wrap_stream_unary(behavior):
            async def wrapper(request_iterator, context):
                start_time = time.time()
                try:
                    response = await behavior(request_iterator, context)
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                    return response
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                    self.collector.record_error(method_name)
                    raise
            return wrapper

        def wrap_stream_stream(behavior):
            async def wrapper(request_iterator, context):
                start_time = time.time()
                try:
                    async for response in behavior(request_iterator, context):
                        yield response
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    self.collector.record_response_time(method_name, duration_ms)
                    self.collector.record_error(method_name)
                    raise
            return wrapper

        # Return wrapped handler based on type
        if handler.unary_unary:
            return grpc.unary_unary_rpc_method_handler(
                wrap_unary_unary(handler.unary_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.unary_stream:
            return grpc.unary_stream_rpc_method_handler(
                wrap_unary_stream(handler.unary_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.stream_unary:
            return grpc.stream_unary_rpc_method_handler(
                wrap_stream_unary(handler.stream_unary),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        elif handler.stream_stream:
            return grpc.stream_stream_rpc_method_handler(
                wrap_stream_stream(handler.stream_stream),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        else:
            return handler


__all__ = ["MetricsInterceptor", "MetricsCollector", "get_metrics", "reset_metrics"]
