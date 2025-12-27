"""
gRPC Configuration Package.

This package provides type-safe configuration classes for gRPC integration.
All configurations use Pydantic v2 with strict validation.

Modules:
    constants: All default values with environment variable support
    tls: TLS/SSL configuration for secure connections
    channels: Client channel configuration
    commands: Command client configuration

Usage:
    from django_cfg.apps.integrations.grpc.configs import (
        TLSConfig,
        ClientChannelConfig,
        CommandClientConfig,
    )

    from django_cfg.apps.integrations.grpc.configs.constants import (
        GRPC_DEFAULT_PORT,
        GRPC_DEFAULT_HOST,
    )

Example:
    # TLS configuration
    tls = TLSConfig(
        enabled=True,
        cert_path="/etc/ssl/server.crt",
        key_path="/etc/ssl/server.key",
    )

    # Client channel configuration
    channel = ClientChannelConfig(
        address="grpc.example.com:443",
        use_tls=True,
        max_retries=5,
    )

    # Command client configuration
    cmd = CommandClientConfig(
        call_timeout=30.0,
    )
"""

from __future__ import annotations

# Core configuration classes (no Django dependencies)
from .channels import ClientChannelConfig
from .commands import CommandClientConfig
from .tls import TLSConfig

__all__ = [
    # New configs
    "TLSConfig",
    "ClientChannelConfig",
    "CommandClientConfig",
]


def __getattr__(name: str):
    """
    Lazy imports for configs that may have Django dependencies.

    This avoids circular imports when importing the configs package
    before Django is fully configured.
    """
    if name == "BidirectionalStreamingConfig":
        from ..services.streaming.config import BidirectionalStreamingConfig
        return BidirectionalStreamingConfig
    elif name == "StreamingMode":
        from ..services.streaming.config import StreamingMode
        return StreamingMode
    elif name == "PingStrategy":
        from ..services.streaming.config import PingStrategy
        return PingStrategy
    elif name == "ConfigPresets":
        from ..services.streaming.config import ConfigPresets
        return ConfigPresets
    elif name == "CrossProcessConfig":
        from ..services.routing.config import CrossProcessConfig
        return CrossProcessConfig
    elif name == "CentrifugoChannels":
        from ..services.centrifugo.config import CentrifugoChannels
        return CentrifugoChannels
    elif name == "ChannelConfig":
        from ..services.centrifugo.config import ChannelConfig
        return ChannelConfig

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
