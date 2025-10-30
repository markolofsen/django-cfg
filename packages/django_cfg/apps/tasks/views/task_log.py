"""
TaskLog ViewSet - Main Entry Point.

Combines all task log functionality through mixins.
"""
from .task_log_base import TaskLogBaseViewSet
from .task_log_stats import TaskLogStatsMixin
from .task_log_timeline import TaskLogTimelineMixin
from .task_log_overview import TaskLogOverviewMixin
from .task_log_related import TaskLogRelatedMixin


class TaskLogViewSet(
    TaskLogStatsMixin,
    TaskLogTimelineMixin,
    TaskLogOverviewMixin,
    TaskLogRelatedMixin,
    TaskLogBaseViewSet,
):
    """
    Complete ViewSet for TaskLog monitoring.

    Provides read-only access to task execution logs with filtering,
    searching, and statistics.

    Endpoints:
        GET /api/tasks/logs/ - List all task logs
        GET /api/tasks/logs/{id}/ - Get task log details
        GET /api/tasks/logs/{id}/related/ - Get related task logs
        GET /api/tasks/logs/stats/ - Get aggregated statistics
        GET /api/tasks/logs/timeline/ - Get task execution timeline
        GET /api/tasks/logs/overview/ - Get summary overview

    Mixins:
        - TaskLogStatsMixin: Aggregated statistics
        - TaskLogTimelineMixin: Time-series data
        - TaskLogOverviewMixin: High-level summary
        - TaskLogRelatedMixin: Related task lookup
        - TaskLogBaseViewSet: Base CRUD operations
    """
    pass
