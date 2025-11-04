"""
Pydantic serializers for gRPC monitoring API.
"""

from .api_keys import (
    ApiKeyListSerializer,
    ApiKeySerializer,
    ApiKeyStatsSerializer,
)
from .proto_files import (
    ProtoFileDetailSerializer,
    ProtoFileListSerializer,
    ProtoGenerateRequestSerializer,
    ProtoGenerateResponseSerializer,
)
from .charts import (
    DashboardChartsSerializer,
    ErrorDistributionChartSerializer,
    RequestVolumeChartSerializer,
    ResponseTimeChartSerializer,
    ServerLifecycleChartSerializer,
    ServerUptimeChartSerializer,
    ServiceActivityChartSerializer,
)
from .config import GRPCConfigSerializer, GRPCServerInfoSerializer
from .health import GRPCHealthCheckSerializer
from .requests import RecentRequestsSerializer
from .service_registry import (
    MethodDetailSerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    ServiceMethodsSerializer,
)
from .services import (
    MethodListSerializer,
    MethodStatsSerializer,
)
from .stats import GRPCOverviewStatsSerializer
from .testing import (
    GRPCCallRequestSerializer,
    GRPCCallResponseSerializer,
    GRPCExamplesListSerializer,
    GRPCTestLogsSerializer,
)

__all__ = [
    # Health & Stats
    "GRPCHealthCheckSerializer",
    "GRPCOverviewStatsSerializer",
    "RecentRequestsSerializer",
    "MethodStatsSerializer",
    "MethodListSerializer",
    # Config
    "GRPCConfigSerializer",
    "GRPCServerInfoSerializer",
    # Service Registry
    "ServiceListSerializer",
    "ServiceDetailSerializer",
    "ServiceMethodsSerializer",
    "MethodDetailSerializer",
    # Testing
    "GRPCExamplesListSerializer",
    "GRPCTestLogsSerializer",
    "GRPCCallRequestSerializer",
    "GRPCCallResponseSerializer",
    # Charts
    "ServerUptimeChartSerializer",
    "RequestVolumeChartSerializer",
    "ResponseTimeChartSerializer",
    "ServiceActivityChartSerializer",
    "ServerLifecycleChartSerializer",
    "ErrorDistributionChartSerializer",
    "DashboardChartsSerializer",
    # API Keys
    "ApiKeySerializer",
    "ApiKeyListSerializer",
    "ApiKeyStatsSerializer",
    # Proto Files
    "ProtoFileDetailSerializer",
    "ProtoFileListSerializer",
    "ProtoGenerateRequestSerializer",
    "ProtoGenerateResponseSerializer",
]
