"""
Dashboard Serializers

Organized by domain for better maintainability.
"""

from .base import APIResponseSerializer
from .statistics import StatCardSerializer, UserStatisticsSerializer, AppStatisticsSerializer
from .system import SystemHealthSerializer, SystemHealthItemSerializer, SystemMetricsSerializer
from .activity import ActivityEntrySerializer, QuickActionSerializer
from .overview import DashboardOverviewSerializer
from .charts import (
    ChartDataSerializer,
    ChartDatasetSerializer,
    ActivityTrackerDaySerializer,
    RecentUserSerializer,
)
from .commands import (
    CommandSerializer,
    CommandsSummarySerializer,
    CommandExecuteRequestSerializer,
    CommandHelpResponseSerializer,
)
from .apizones import APIZoneSerializer, APIZonesSummarySerializer
from .django_q2 import (
    DjangoQ2ScheduleSerializer,
    DjangoQ2TaskSerializer,
    DjangoQ2StatusSerializer,
    DjangoQ2SummarySerializer,
)

__all__ = [
    # Base
    'APIResponseSerializer',

    # Statistics
    'StatCardSerializer',
    'UserStatisticsSerializer',
    'AppStatisticsSerializer',

    # System
    'SystemHealthSerializer',
    'SystemHealthItemSerializer',
    'SystemMetricsSerializer',

    # Activity
    'ActivityEntrySerializer',
    'QuickActionSerializer',

    # Overview
    'DashboardOverviewSerializer',

    # Charts
    'ChartDataSerializer',
    'ChartDatasetSerializer',
    'ActivityTrackerDaySerializer',
    'RecentUserSerializer',

    # Commands
    'CommandSerializer',
    'CommandsSummarySerializer',
    'CommandExecuteRequestSerializer',
    'CommandHelpResponseSerializer',

    # API Zones
    'APIZoneSerializer',
    'APIZonesSummarySerializer',

    # Django-Q2
    'DjangoQ2ScheduleSerializer',
    'DjangoQ2TaskSerializer',
    'DjangoQ2StatusSerializer',
    'DjangoQ2SummarySerializer',
]
