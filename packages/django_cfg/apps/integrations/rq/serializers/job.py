"""
Job information serializers for Django-RQ.
"""

from rest_framework import serializers


class JobListSerializer(serializers.Serializer):
    """
    Job list item serializer.

    Provides basic job information for list views.
    """

    id = serializers.CharField(help_text="Job ID")
    func_name = serializers.CharField(help_text="Function name")
    created_at = serializers.DateTimeField(help_text="Job creation time")
    status = serializers.CharField(
        help_text="Job status (queued/started/finished/failed)"
    )
    queue = serializers.CharField(help_text="Queue name")
    timeout = serializers.IntegerField(
        allow_null=True, required=False, help_text="Job timeout in seconds"
    )


class JobDetailSerializer(serializers.Serializer):
    """
    Detailed job information serializer.

    Provides comprehensive job details including result and metadata.
    """

    id = serializers.CharField(help_text="Job ID")
    func_name = serializers.CharField(help_text="Function name")
    args = serializers.ListField(
        child=serializers.JSONField(),
        default=list,
        help_text="Function arguments (array of any JSON values)"
    )
    kwargs = serializers.JSONField(default=dict, help_text="Function keyword arguments")

    # Status and timing
    created_at = serializers.DateTimeField(help_text="Job creation time")
    enqueued_at = serializers.DateTimeField(
        allow_null=True, required=False, help_text="Job enqueue time"
    )
    started_at = serializers.DateTimeField(
        allow_null=True, required=False, help_text="Job start time"
    )
    ended_at = serializers.DateTimeField(
        allow_null=True, required=False, help_text="Job end time"
    )
    status = serializers.CharField(
        help_text="Job status (queued/started/finished/failed)"
    )

    # Queue and worker
    queue = serializers.CharField(help_text="Queue name")
    worker_name = serializers.CharField(
        allow_null=True, required=False, help_text="Worker name if started"
    )

    # Configuration
    timeout = serializers.IntegerField(
        allow_null=True, required=False, help_text="Job timeout in seconds"
    )
    result_ttl = serializers.IntegerField(
        allow_null=True, required=False, help_text="Result TTL in seconds"
    )
    failure_ttl = serializers.IntegerField(
        allow_null=True, required=False, help_text="Failure TTL in seconds"
    )

    # Result and error
    result = serializers.JSONField(
        allow_null=True, required=False, help_text="Job result if finished"
    )
    exc_info = serializers.CharField(
        allow_null=True, required=False, help_text="Exception info if failed"
    )

    # Metadata
    meta = serializers.JSONField(default=dict, help_text="Job metadata")
    dependency_ids = serializers.ListField(
        child=serializers.CharField(),
        default=list,
        help_text="List of dependency job IDs",
    )


class JobActionResponseSerializer(serializers.Serializer):
    """
    Job action response serializer.

    Used for job management actions (requeue, delete, etc.).
    """

    success = serializers.BooleanField(help_text="Action success status")
    message = serializers.CharField(help_text="Action result message")
    job_id = serializers.CharField(help_text="Job ID")
    action = serializers.CharField(
        help_text="Action performed (requeue/delete/cancel)"
    )
