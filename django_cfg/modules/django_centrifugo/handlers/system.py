"""
System RPC handlers for Centrifugo.

Built-in handlers for system operations like version checking.
"""

import logging
from pydantic import BaseModel, Field

from ..decorators import websocket_rpc
from ..registry import get_global_registry

logger = logging.getLogger(__name__)


class CheckVersionParams(BaseModel):
    """Parameters for version check."""

    client_version: str = Field(..., description="Client API version hash")


class VersionCheckResult(BaseModel):
    """Result of version compatibility check."""

    compatible: bool = Field(..., description="Whether versions are compatible")
    client_version: str = Field(..., description="Client version received")
    server_version: str = Field(..., description="Server API version hash")
    message: str = Field(default="", description="Additional info message")


@websocket_rpc("system.check_version")
async def check_version(conn, params: CheckVersionParams) -> VersionCheckResult:
    """
    Check if client API version is compatible with server.

    Computes server API version hash and compares with client.
    Returns compatibility status and version info.
    """
    registry = get_global_registry()
    server_version = registry.compute_api_version()

    compatible = params.client_version == server_version

    if compatible:
        message = "API versions match"
    else:
        message = (
            f"API version mismatch! Client: {params.client_version}, "
            f"Server: {server_version}. Please regenerate the client."
        )
        logger.warning(
            f"API version mismatch for user {conn.user_id}: "
            f"client={params.client_version}, server={server_version}"
        )

    return VersionCheckResult(
        compatible=compatible,
        client_version=params.client_version,
        server_version=server_version,
        message=message,
    )


__all__ = [
    "CheckVersionParams",
    "VersionCheckResult",
    "check_version",
]
