"""
TaskLog DRF Serializers.

Serializers for TaskLog model with filtering and statistics.
"""
from rest_framework import serializers
from ..models import TaskLog


class TaskLogSerializer(serializers.ModelSerializer):
    """
    Basic TaskLog serializer.

    Used for list views with essential fields only.
    Includes computed properties matching ReArq response format.
    """

    duration_seconds = serializers.SerializerMethodField()
    is_completed = serializers.BooleanField(read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)

    class Meta:
        model = TaskLog
        fields = [
            'id',
            'job_id',
            'task_name',
            'queue_name',
            'status',
            'success',
            'duration_ms',
            'duration_seconds',
            'job_retry',
            'job_retries',
            'enqueue_time',
            'expire_time',
            'start_time',
            'finish_time',
            'is_completed',
            'is_successful',
            'is_failed',
        ]
        read_only_fields = fields

    def get_duration_seconds(self, obj) -> float:
        """Convert duration from ms to seconds."""
        if obj.duration_ms is not None:
            return round(obj.duration_ms / 1000, 2)
        return None


class TaskLogListSerializer(serializers.ModelSerializer):
    """
    Compact serializer for list views.

    Minimal fields for performance, matching ReArq Job list format.
    """

    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = TaskLog
        fields = [
            'id',
            'job_id',
            'task_name',
            'queue_name',
            'status',
            'status_display',
            'success',
            'job_retries',
            'duration_ms',
            'enqueue_time',
            'start_time',
            'finish_time',
        ]
        read_only_fields = fields


class TaskLogDetailSerializer(serializers.ModelSerializer):
    """
    Detailed TaskLog serializer.

    Includes all fields including args, kwargs, result, error messages.
    Combines ReArq Job + JobResult data.
    """

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_seconds = serializers.SerializerMethodField()
    user_display = serializers.SerializerMethodField()

    class Meta:
        model = TaskLog
        fields = [
            # Job identification
            'id',
            'job_id',
            'task_name',
            'queue_name',
            # Status
            'status',
            'status_display',
            'success',
            # Arguments
            'args',
            'kwargs',
            # Result
            'result',
            'error_message',
            # Performance
            'duration_ms',
            'duration_seconds',
            # Retry info (from ReArq Job)
            'job_retry',
            'job_retries',
            'job_retry_after',
            # Worker
            'worker_id',
            # Timestamps (from ReArq)
            'enqueue_time',
            'expire_time',
            'start_time',
            'finish_time',
            # Django timestamps
            'created_at',
            'updated_at',
            # User
            'user',
            'user_display',
        ]
        read_only_fields = fields

    def get_duration_seconds(self, obj) -> float:
        """Convert duration from ms to seconds."""
        if obj.duration_ms is not None:
            return round(obj.duration_ms / 1000, 2)
        return None

    def get_user_display(self, obj) -> str:
        """Get user display name."""
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return None


class TaskLogStatsSerializer(serializers.Serializer):
    """
    Statistics serializer for task metrics.

    Not tied to a model - used for aggregated data.
    """

    total = serializers.IntegerField(help_text="Total number of task executions")
    successful = serializers.IntegerField(help_text="Number of successful executions")
    failed = serializers.IntegerField(help_text="Number of failed executions")
    in_progress = serializers.IntegerField(help_text="Number of tasks currently running")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    avg_duration_ms = serializers.IntegerField(help_text="Average duration in milliseconds")
    avg_duration_seconds = serializers.FloatField(help_text="Average duration in seconds")
    period_hours = serializers.IntegerField(help_text="Statistics period in hours", required=False)


class TasksByQueueSerializer(serializers.Serializer):
    """
    Tasks count by queue.

    Used in overview endpoint for tasks_by_queue list.
    """
    queue_name = serializers.CharField(help_text="Queue name")
    count = serializers.IntegerField(help_text="Number of tasks in this queue")


class TasksByStatusSerializer(serializers.Serializer):
    """
    Tasks count by status.

    Used in overview endpoint for tasks_by_status list.
    """
    status = serializers.CharField(help_text="Task status")
    count = serializers.IntegerField(help_text="Number of tasks with this status")


class TaskLogOverviewSerializer(serializers.Serializer):
    """
    Overview of task system with proper structure.

    Provides high-level statistics about the entire task system:
    - Total tasks count (all-time)
    - Active queues list
    - Recent failures (last 24h)
    - Tasks distribution by queue (as array)
    - Tasks distribution by status (as array)

    Used by /cfg/tasks/logs/overview/ endpoint.
    """
    total_tasks = serializers.IntegerField(help_text="Total number of tasks all-time")
    active_queues = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of active queue names"
    )
    recent_failures = serializers.IntegerField(help_text="Failed tasks in last 24 hours")
    tasks_by_queue = TasksByQueueSerializer(
        many=True,
        help_text="Tasks grouped by queue name"
    )
    tasks_by_status = TasksByStatusSerializer(
        many=True,
        help_text="Tasks grouped by status"
    )


class TaskLogTimelineItemSerializer(serializers.Serializer):
    """
    Single timeline data point.

    Represents aggregated task statistics for a specific time period.
    """
    timestamp = serializers.DateTimeField(help_text="Time bucket start")
    total = serializers.IntegerField(help_text="Total tasks in this period")
    successful = serializers.IntegerField(help_text="Successful tasks")
    failed = serializers.IntegerField(help_text="Failed tasks")
    in_progress = serializers.IntegerField(help_text="Tasks currently in progress", required=False)
    avg_duration_ms = serializers.FloatField(help_text="Average duration in milliseconds", required=False)


class TaskLogTimelineSerializer(serializers.Serializer):
    """
    Timeline response wrapper.

    Returns timeline data as array of time-bucketed statistics.
    Used by /cfg/tasks/logs/timeline/ endpoint.
    """
    period_hours = serializers.IntegerField(help_text="Time period covered in hours")
    interval = serializers.CharField(help_text="Time bucket interval (hour/day)")
    data = TaskLogTimelineItemSerializer(many=True, help_text="Timeline data points")


__all__ = [
    "TaskLogSerializer",
    "TaskLogListSerializer",
    "TaskLogDetailSerializer",
    "TaskLogStatsSerializer",
    "TasksByQueueSerializer",
    "TasksByStatusSerializer",
    "TaskLogOverviewSerializer",
    "TaskLogTimelineItemSerializer",
    "TaskLogTimelineSerializer",
]
