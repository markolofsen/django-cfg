"""
Schedule management serializers for Django-RQ.
"""

from rest_framework import serializers


class ScheduleCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a scheduled job.

    Supports three scheduling methods:
    1. scheduled_time: Schedule job at specific time
    2. interval: Schedule job to repeat at intervals
    3. cron: Schedule job with cron expression
    """

    # Job configuration
    func = serializers.CharField(
        help_text="Function path (e.g., 'myapp.tasks.my_task')"
    )
    args = serializers.ListField(
        child=serializers.JSONField(),
        default=list,
        required=False,
        help_text="Function arguments (array of any JSON values)"
    )
    kwargs = serializers.JSONField(
        default=dict,
        required=False,
        help_text="Function keyword arguments"
    )

    # Queue configuration
    queue_name = serializers.CharField(
        default="default",
        help_text="Queue name to schedule job in"
    )

    # Scheduling options (choose one)
    scheduled_time = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Schedule job at specific time (ISO 8601)"
    )
    interval = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="Schedule job to repeat every N seconds"
    )
    cron = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Cron expression (e.g., '0 0 * * *' for daily at midnight)"
    )

    # Job options
    timeout = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Job timeout in seconds"
    )
    result_ttl = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Result TTL in seconds"
    )
    repeat = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Number of times to repeat (None = infinite)"
    )
    description = serializers.CharField(
        required=False,
        allow_null=True,
        max_length=255,
        help_text="Job description"
    )

    def validate(self, attrs):
        """Validate that exactly one scheduling method is provided."""
        scheduling_methods = [
            attrs.get('scheduled_time'),
            attrs.get('interval'),
            attrs.get('cron'),
        ]
        provided_methods = [m for m in scheduling_methods if m is not None]

        if len(provided_methods) == 0:
            raise serializers.ValidationError(
                "Must provide one of: scheduled_time, interval, or cron"
            )

        if len(provided_methods) > 1:
            raise serializers.ValidationError(
                "Can only provide one scheduling method: scheduled_time, interval, or cron"
            )

        return attrs


class ScheduledJobSerializer(serializers.Serializer):
    """
    Serializer for scheduled job information.
    """

    id = serializers.CharField(help_text="Job ID")
    func = serializers.CharField(help_text="Function path")
    args = serializers.ListField(
        child=serializers.JSONField(),
        default=list,
        help_text="Function arguments (array of any JSON values)"
    )
    kwargs = serializers.JSONField(default=dict, help_text="Function keyword arguments")

    # Schedule info
    queue_name = serializers.CharField(help_text="Queue name")
    scheduled_time = serializers.DateTimeField(
        allow_null=True,
        required=False,
        help_text="Next scheduled time"
    )
    interval = serializers.IntegerField(
        allow_null=True,
        required=False,
        help_text="Repeat interval in seconds"
    )
    cron = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Cron expression"
    )

    # Job options
    timeout = serializers.IntegerField(
        allow_null=True,
        required=False,
        help_text="Job timeout in seconds"
    )
    result_ttl = serializers.IntegerField(
        allow_null=True,
        required=False,
        help_text="Result TTL in seconds"
    )
    repeat = serializers.IntegerField(
        allow_null=True,
        required=False,
        help_text="Times to repeat (None = infinite)"
    )
    description = serializers.CharField(
        allow_null=True,
        required=False,
        help_text="Job description"
    )

    # Metadata
    created_at = serializers.DateTimeField(
        allow_null=True,
        required=False,
        help_text="Job creation time"
    )
    meta = serializers.JSONField(
        default=dict,
        help_text="Job metadata"
    )


class ScheduleActionResponseSerializer(serializers.Serializer):
    """
    Response serializer for schedule actions (create/delete).
    """

    success = serializers.BooleanField(help_text="Action success status")
    message = serializers.CharField(help_text="Action result message")
    job_id = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Job ID (for create action)"
    )
    action = serializers.CharField(
        help_text="Action performed (create/delete/cancel)"
    )
