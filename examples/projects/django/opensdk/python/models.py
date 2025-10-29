"""
Generated Pydantic Models.

Auto-generated from RPC handler type hints - DO NOT EDIT
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class UserPresenceParams(BaseModel):
    """User presence update parameters."""
    user_id: str = Field(..., description='User ID')
    status: str = Field(..., description='Status: online, away, busy, offline')


class HealthCheckResult(BaseModel):
    """Health check response."""
    status: str = Field(..., description='System status: healthy, degraded, unhealthy')
    uptime_seconds: int = Field(..., description='System uptime in seconds')
    database: str = Field(..., description='Database status')
    cache: str = Field(..., description='Cache status')


class HealthCheckParams(BaseModel):
    """Health check request parameters."""
    include_details: Optional[bool] = Field(None, description='Include detailed system info')


class UserPresenceResult(BaseModel):
    """User presence response."""
    user_id: str = Field(..., description='User ID')
    status: str = Field(..., description='Current status')
    last_seen: str = Field(..., description='Last seen timestamp (ISO 8601)')



__all__ = [
    "UserPresenceParams",
    "HealthCheckResult",
    "HealthCheckParams",
    "UserPresenceResult",
]