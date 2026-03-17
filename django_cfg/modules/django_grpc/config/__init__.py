"""django_grpc.config — gRPC configuration models and constants."""

from .auth import GrpcAuthConfig
from .client import ClientChannelConfig
from .commands import CommandClientConfig
from .constants import (
    GRPC_BIND_HOST_IPV4,
    GRPC_BIND_HOST_IPV6,
    GRPC_DEFAULT_HOST,
    GRPC_DEFAULT_PORT,
    get_bind_address,
    get_grpc_address,
    get_grpc_host,
    get_grpc_port,
)
from .metrics import MetricsConfig
from .observability import CentrifugoPublishConfig, ObservabilityConfig, TelegramNotifyConfig
from .persistence import GrpcPersistenceConfig, LogWorkerConfig
from .pool import GrpcPoolConfig
from .resilience import CircuitBreakerConfig, ResilienceConfig, RetryConfig
from .routing import CrossProcessConfig
from .server import GrpcKeepaliveConfig, GrpcServerConfig
from .streaming import BidirectionalStreamingConfig, ConfigPresets, PingStrategy, StreamingMode
from .tls import TLSConfig

__all__ = [
    # Server
    "GrpcServerConfig",
    "GrpcKeepaliveConfig",
    # Auth
    "GrpcAuthConfig",
    # Streaming
    "BidirectionalStreamingConfig",
    "StreamingMode",
    "PingStrategy",
    "ConfigPresets",
    # Resilience
    "ResilienceConfig",
    "RetryConfig",
    "CircuitBreakerConfig",
    # Pool (unified — replaces old PoolConfig)
    "GrpcPoolConfig",
    # Commands
    "CommandClientConfig",
    # Persistence + log worker
    "GrpcPersistenceConfig",
    "LogWorkerConfig",
    # Observability
    "ObservabilityConfig",
    "CentrifugoPublishConfig",
    "TelegramNotifyConfig",
    # Metrics
    "MetricsConfig",
    # Routing
    "CrossProcessConfig",
    # Client
    "ClientChannelConfig",
    # TLS
    "TLSConfig",
    # Constants
    "GRPC_DEFAULT_HOST",
    "GRPC_DEFAULT_PORT",
    "GRPC_BIND_HOST_IPV6",
    "GRPC_BIND_HOST_IPV4",
    "get_grpc_host",
    "get_grpc_port",
    "get_grpc_address",
    "get_bind_address",
]
