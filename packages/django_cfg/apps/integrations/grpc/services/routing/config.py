"""
Configuration for cross-process command routing.

This module provides Pydantic configuration models without gRPC dependencies.

Created: 2025-11-07
Status: %%PRODUCTION%%
Phase: Phase 1 - Universal Components
"""

from pydantic import BaseModel, Field

from ...configs.constants import (
    GRPC_DEFAULT_HOST,
    GRPC_DEFAULT_PORT,
    GRPC_ROUTING_TIMEOUT,
)


# ============================================================================
# Configuration
# ============================================================================

class CrossProcessConfig(BaseModel):
    """
    Configuration for cross-process command routing.

    **Parameters**:
        grpc_host: gRPC server host (usually "localhost")
        grpc_port: gRPC server port
        rpc_method_name: Name of RPC method to call (e.g., "SendCommandToBot")
        timeout: Timeout for gRPC calls in seconds
        enable_logging: Enable detailed logging

    **Example**:
    ```python
    config = CrossProcessConfig(
        grpc_host="localhost",
        grpc_port=50051,
        rpc_method_name="SendCommandToClient",
        timeout=5.0,
    )
    ```
    """

    grpc_host: str = Field(
        default=GRPC_DEFAULT_HOST,
        description="gRPC server host",
    )

    grpc_port: int = Field(
        default=GRPC_DEFAULT_PORT,
        gt=0,
        le=65535,
        description="gRPC server port (1-65535)",
    )

    rpc_method_name: str = Field(
        min_length=1,
        description="Name of RPC method for cross-process calls",
    )

    timeout: float = Field(
        default=GRPC_ROUTING_TIMEOUT,
        gt=0.0,
        le=60.0,
        description="Timeout for gRPC calls in seconds",
    )

    enable_logging: bool = Field(
        default=True,
        description="Enable detailed logging",
    )

    model_config = {
        'extra': 'forbid',
        'frozen': True,
    }

    @property
    def grpc_address(self) -> str:
        """Get full gRPC address (host:port)."""
        return f"{self.grpc_host}:{self.grpc_port}"
