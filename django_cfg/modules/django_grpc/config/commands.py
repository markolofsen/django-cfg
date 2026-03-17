"""
django_grpc.config.commands — Command client configuration.

Configuration for command execution client (same-process queue + cross-process gRPC).
"""

from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CommandClientConfig(BaseModel):
    """
    Configuration for command client execution.

    Supports two execution modes:
    1. Same-process mode: Uses an async queue for communication
    2. Cross-process mode: Uses gRPC RPC for remote execution
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    queue_timeout: float = Field(default=10.0, gt=0.0, le=300.0, description="Timeout for same-process queue operations (s)")
    connect_timeout: float = Field(default=3.0, gt=0.0, le=60.0, description="Timeout for establishing gRPC connection (s)")
    call_timeout: float = Field(default=5.0, gt=0.0, le=600.0, description="Timeout for gRPC RPC call (s)")
    grpc_host: str = Field(default="localhost", description="gRPC server host for cross-process mode")
    grpc_port: int = Field(default=0, ge=0, le=65535, description="gRPC server port for cross-process mode (0 = inherit from GrpcServerConfig.port)")

    @model_validator(mode="before")
    @classmethod
    def _inherit_server_port(cls, data: Any) -> Any:
        """C-03: inherit server.port when grpc_port is not explicitly set."""
        if isinstance(data, dict) and "grpc_port" not in data:
            try:
                from django_cfg.modules.django_grpc.services.management.config_helper import (
                    get_grpc_server_config,
                )
                server_cfg = get_grpc_server_config()
                if server_cfg is not None:
                    data = {**data, "grpc_port": server_cfg.port}
            except Exception:
                pass
        return data

    @property
    def grpc_address(self) -> str:
        return f"{self.grpc_host}:{self.grpc_port}"

    def with_overrides(
        self,
        queue_timeout: float | None = None,
        connect_timeout: float | None = None,
        call_timeout: float | None = None,
        grpc_host: str | None = None,
        grpc_port: int | None = None,
    ) -> Self:
        return self.model_copy(update={
            k: v for k, v in {
                "queue_timeout": queue_timeout,
                "connect_timeout": connect_timeout,
                "call_timeout": call_timeout,
                "grpc_host": grpc_host,
                "grpc_port": grpc_port,
            }.items()
            if v is not None
        })


__all__ = ["CommandClientConfig"]
