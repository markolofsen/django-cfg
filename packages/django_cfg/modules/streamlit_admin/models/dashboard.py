"""Dashboard data models for Streamlit admin.

Pydantic v2 models for dashboard statistics, health status, and metrics.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ChangeType(str, Enum):
    """Change direction for stat cards."""

    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class HealthStatus(str, Enum):
    """System health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"


class StatCard(BaseModel):
    """Dashboard statistics card."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    title: str
    value: str
    change: str | None = None
    change_type: ChangeType = ChangeType.NEUTRAL
    icon: str = "chart"
    color: str | None = None


class ComponentHealth(BaseModel):
    """Health status of a system component."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    name: str
    status: HealthStatus
    message: str | None = None


class SystemHealth(BaseModel):
    """Overall system health."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
    )

    percentage: float = Field(ge=0, le=100)
    status: HealthStatus
    components: list[ComponentHealth] = []
    updated_at: datetime = Field(default_factory=datetime.now)


class MetricPoint(BaseModel):
    """Single metric data point for timeline."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    timestamp: str  # ISO timestamp
    count: int = 0
    successful: int = 0
    failed: int = 0


class SystemMetrics(BaseModel):
    """System metrics from monitoring APIs."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    # Timeline data
    rq_timeline: list[MetricPoint] = []
    centrifugo_timeline: list[MetricPoint] = []
    grpc_timeline: list[MetricPoint] = []

    # Overview stats
    rq_total: int = 0
    rq_success_rate: float = 0.0
    centrifugo_total: int = 0
    centrifugo_success_rate: float = 0.0
    grpc_total: int = 0
    grpc_success_rate: float = 0.0


class QuickAction(BaseModel):
    """Quick action button configuration."""

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    label: str
    icon: str
    url: str | None = None
    action: str | None = None
    color: str = "primary"
    category: str | None = None
