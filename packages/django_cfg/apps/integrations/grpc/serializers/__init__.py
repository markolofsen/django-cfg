"""
Pydantic serializers for gRPC monitoring API.
"""

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
    ServiceListSerializer as ServiceRegistryListSerializer,
    ServiceMethodsSerializer,
)
from .services import (
    MethodListSerializer,
    MethodStatsSerializer,
    MonitoringServiceStatsSerializer,
    ServiceListSerializer,
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
    "MonitoringServiceStatsSerializer",
    "ServiceListSerializer",
    "MethodStatsSerializer",
    "MethodListSerializer",
    # Config
    "GRPCConfigSerializer",
    "GRPCServerInfoSerializer",
    # Service Registry
    "ServiceRegistryListSerializer",
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
]
