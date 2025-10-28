from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import SystemHealthOverallStatus


class SystemHealth(BaseModel):
    """
    Serializer for overall system health status.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    overall_status: SystemHealthOverallStatus = Field(description='Overall system health status\n\n* `healthy` - healthy\n* `warning` - warning\n* `error` - error\n* `unknown` - unknown')
    overall_health_percentage: int = Field(description='Overall health percentage', ge=0, le=100)
    components: list[Any] = Field(description='Health status of individual components')
    timestamp: str = Field(description='Check timestamp (ISO format)')



class SystemMetrics(BaseModel):
    """
    Serializer for system performance metrics.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    cpu_usage: float = Field(description='CPU usage percentage')
    memory_usage: float = Field(description='Memory usage percentage')
    disk_usage: float = Field(description='Disk usage percentage')
    network_in: str = Field(description='Network incoming bandwidth')
    network_out: str = Field(description='Network outgoing bandwidth')
    response_time: str = Field(description='Average response time')
    uptime: str = Field(description='System uptime')



