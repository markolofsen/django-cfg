"""
Configuration for Crypto gRPC service.

Defines service-level settings for price streaming and Centrifugo integration.

Created: 2025-01-08
Status: %%PRODUCTION%%
"""

from dataclasses import dataclass


@dataclass
class CryptoServiceConfig:
    """
    Configuration for Crypto gRPC service.

    Attributes:
        enable_centrifugo: Enable WebSocket publishing via Centrifugo
        price_stream_interval: Interval (seconds) between price updates in StreamPrices
        max_concurrent_streams: Maximum concurrent price streams per client
        enable_logging: Enable detailed logging
        logger_name: Logger name for service
    """

    # Centrifugo integration
    enable_centrifugo: bool = True

    # Price streaming configuration
    price_stream_interval: float = 1.0  # 1 second between updates
    max_concurrent_streams: int = 100  # Max 100 concurrent streams

    # Logging
    enable_logging: bool = True
    logger_name: str = "crypto_grpc_service"


# Default production configuration
ProductionConfig = CryptoServiceConfig(
    enable_centrifugo=True,
    price_stream_interval=1.0,
    max_concurrent_streams=100,
    enable_logging=True,
)

# Testing configuration
TestingConfig = CryptoServiceConfig(
    enable_centrifugo=False,  # No WebSocket in tests
    price_stream_interval=0.1,  # Faster updates for tests
    max_concurrent_streams=10,
    enable_logging=False,
)

