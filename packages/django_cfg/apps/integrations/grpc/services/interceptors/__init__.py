"""
gRPC interceptors for Django applications.

Provides production-ready interceptors for gRPC services with support for:
- Bidirectional streaming (ObservabilityInterceptor)
- Error handling (ErrorHandlingInterceptor)
- Metrics collection (get_metrics, reset_metrics)

Usage:
    ```python
    GRPC_FRAMEWORK = {
        "SERVER_INTERCEPTORS": [
            # Order matters! Auth first (sets contextvars), then Observability
            "django_cfg.apps.integrations.grpc.auth.ApiKeyAuthInterceptor",
            "django_cfg.apps.integrations.grpc.services.interceptors.ObservabilityInterceptor",
        ]
    }
    ```

Note:
    ObservabilityInterceptor combines metrics, logging, request logging, and
    Centrifugo publishing into a single interceptor. This is required for
    bidirectional streaming - using separate interceptors creates nested
    async generators that cause StopAsyncIteration after ~15 messages.
"""

from .errors import ErrorHandlingInterceptor
from .observability import ObservabilityInterceptor, get_metrics, reset_metrics
from .metrics import MetricsCollector, get_metrics_collector
from .wrapped_handler import WrappedHandler
from .db_logger import RequestLogger
from .publishers import EventPublisher

__all__ = [
    # Main interceptors
    "ObservabilityInterceptor",
    "ErrorHandlingInterceptor",
    # Metrics
    "get_metrics",
    "reset_metrics",
    "MetricsCollector",
    "get_metrics_collector",
    # Components (for advanced usage)
    "WrappedHandler",
    "RequestLogger",
    "EventPublisher",
]
