"""Streamlit Admin Types - Re-exports from generated API models.

Provides typed access to API models decomposed by domain:
- accounts: User, profile, auth types
- rq: Queue, worker, job types
- centrifugo: Channel, publish types
- grpc: Service, method types
- totp: Device, backup codes types
- enums: All enumeration types

Usage:
    from streamlit_admin.api.types import User, QueueStats, Worker
    from streamlit_admin.api.types.rq import JobDetail, JobList
    from streamlit_admin.api.types.enums import DeviceListStatus
"""

from .accounts import (
    AccountDeleteResponse,
    CentrifugoToken,
    User,
    UserProfileUpdateRequest,
)
from .centrifugo import (
    CentrifugoHealthCheck,
    CentrifugoOverviewStats,
    ChannelList,
    ChannelStats,
    Publish,
    TimelineItem,
    TimelineResponse,
)
from .enums import (
    CfgRqTestingScheduleDemoCreateRequestScheduleType,
    DeviceListStatus,
    OAuthConnectionProvider,
    OTPRequestRequestChannel,
    RunDemoRequestRequestScenario,
    StressTestRequestRequestScenario,
)
from .grpc import (
    GRPCServiceRegistryMethodStats,
    MethodInfo,
    MethodSummary,
    RecentError,
    ServiceDetail,
    ServiceMethods,
    ServiceStats,
    ServiceSummary,
)
from .rq import (
    JobActionResponse,
    JobDetail,
    JobList,
    QueueDetail,
    QueueStats,
    ScheduleActionResponse,
    ScheduleCreateRequest,
    ScheduledJob,
    Worker,
    WorkerStats,
)
from .totp import (
    BackupCodesRegenerateRequest,
    BackupCodesRegenerateResponse,
    BackupCodesStatus,
    DeviceList,
    DeviceListResponse,
    DisableRequest,
)

__all__ = [
    # Accounts
    "User",
    "CentrifugoToken",
    "UserProfileUpdateRequest",
    "AccountDeleteResponse",
    # RQ
    "QueueStats",
    "QueueDetail",
    "Worker",
    "WorkerStats",
    "JobList",
    "JobDetail",
    "JobActionResponse",
    "ScheduledJob",
    "ScheduleCreateRequest",
    "ScheduleActionResponse",
    # Centrifugo
    "ChannelStats",
    "ChannelList",
    "CentrifugoHealthCheck",
    "CentrifugoOverviewStats",
    "Publish",
    "TimelineItem",
    "TimelineResponse",
    # gRPC
    "ServiceSummary",
    "ServiceDetail",
    "ServiceStats",
    "ServiceMethods",
    "MethodInfo",
    "MethodSummary",
    "GRPCServiceRegistryMethodStats",
    "RecentError",
    # TOTP
    "DeviceList",
    "DeviceListResponse",
    "DisableRequest",
    "BackupCodesStatus",
    "BackupCodesRegenerateRequest",
    "BackupCodesRegenerateResponse",
    # Enums
    "DeviceListStatus",
    "OAuthConnectionProvider",
    "OTPRequestRequestChannel",
    "RunDemoRequestRequestScenario",
    "StressTestRequestRequestScenario",
    "CfgRqTestingScheduleDemoCreateRequestScheduleType",
]
