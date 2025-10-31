"""
Dashboard Views

ViewSets organized by domain for better maintainability.
"""

from .overview_views import OverviewViewSet
from .statistics_views import StatisticsViewSet
from .system_views import SystemViewSet
from .activity_views import ActivityViewSet
from .charts_views import ChartsViewSet
from .commands_views import CommandsViewSet
from .apizones_views import APIZonesViewSet
from .crontab_views import CrontabViewSet

__all__ = [
    'OverviewViewSet',
    'StatisticsViewSet',
    'SystemViewSet',
    'ActivityViewSet',
    'ChartsViewSet',
    'CommandsViewSet',
    'APIZonesViewSet',
    'CrontabViewSet',
]
