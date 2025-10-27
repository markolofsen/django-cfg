"""
Centrifugo WebSocket RPC Handlers.

These handlers are auto-discovered and used to generate type-safe clients.
"""

from typing import Optional
from pydantic import BaseModel, Field
from django_cfg.apps.centrifugo.decorators import websocket_rpc


# System Health Check
class HealthCheckParams(BaseModel):
    """Health check request parameters."""
    include_details: bool = Field(False, description="Include detailed system info")


class HealthCheckResult(BaseModel):
    """Health check response."""
    status: str = Field(..., description="System status: healthy, degraded, unhealthy")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    database: str = Field(..., description="Database status")
    cache: str = Field(..., description="Cache status")


@websocket_rpc("system.health")
async def health_check(conn, params: HealthCheckParams) -> HealthCheckResult:
    """
    Check system health status.

    Returns current status of all system components including
    database, cache, and overall health.
    """
    # TODO: Implement actual health checks
    return HealthCheckResult(
        status="healthy",
        uptime_seconds=3600,
        database="connected",
        cache="connected"
    )


# User Presence
class UserPresenceParams(BaseModel):
    """User presence update parameters."""
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Status: online, away, busy, offline")


class UserPresenceResult(BaseModel):
    """User presence response."""
    user_id: str = Field(..., description="User ID")
    status: str = Field(..., description="Current status")
    last_seen: str = Field(..., description="Last seen timestamp (ISO 8601)")


@websocket_rpc("users.update_presence")
async def update_user_presence(conn, params: UserPresenceParams) -> UserPresenceResult:
    """
    Update user presence status.

    Updates the user's online status and broadcasts to subscribers.
    """
    from datetime import datetime

    # TODO: Implement actual presence logic
    return UserPresenceResult(
        user_id=params.user_id,
        status=params.status,
        last_seen=datetime.utcnow().isoformat()
    )
