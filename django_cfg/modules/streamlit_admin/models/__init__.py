"""Streamlit Admin data models.

Pydantic v2 models for dashboard, RQ, and other admin components.
"""

from .centrifugo import CentrifugoHealth, ChannelInfo, PublishRecord
from .config import StreamlitAdminConfig
from .dashboard import (
    ChangeType,
    ComponentHealth,
    HealthStatus,
    MetricPoint,
    QuickAction,
    StatCard,
    SystemHealth,
    SystemMetrics,
)
from .grpc import GRPCHealth, MethodStats, ServiceInfo
from .rq import (
    JobInfo,
    JobStatus,
    QueueStats,
    ScheduledJob,
    WorkerInfo,
)
from .users import UserInfo, UserProfile

__all__ = [
    # Config
    "StreamlitAdminConfig",
    # Dashboard
    "ChangeType",
    "HealthStatus",
    "StatCard",
    "ComponentHealth",
    "SystemHealth",
    "MetricPoint",
    "SystemMetrics",
    "QuickAction",
    # RQ
    "JobStatus",
    "QueueStats",
    "WorkerInfo",
    "JobInfo",
    "ScheduledJob",
    # Centrifugo
    "ChannelInfo",
    "CentrifugoHealth",
    "PublishRecord",
    # gRPC
    "ServiceInfo",
    "MethodStats",
    "GRPCHealth",
    # Users
    "UserInfo",
    "UserProfile",
]
