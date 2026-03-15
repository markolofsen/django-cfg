"""
Queue statistics serializers for Django-RQ.
"""

from rest_framework import serializers


class QueueStatsSerializer(serializers.Serializer):
    """
    Queue statistics serializer.

    Provides basic queue statistics.
    """

    name = serializers.CharField(help_text="Queue name")
    count = serializers.IntegerField(help_text="Total jobs in queue")
    queued_jobs = serializers.IntegerField(
        default=0, help_text="Jobs waiting to be processed"
    )
    started_jobs = serializers.IntegerField(
        default=0, help_text="Jobs currently being processed"
    )
    finished_jobs = serializers.IntegerField(default=0, help_text="Completed jobs")
    failed_jobs = serializers.IntegerField(default=0, help_text="Failed jobs")
    deferred_jobs = serializers.IntegerField(default=0, help_text="Deferred jobs")
    scheduled_jobs = serializers.IntegerField(default=0, help_text="Scheduled jobs")
    workers = serializers.IntegerField(
        default=0, help_text="Number of workers for this queue"
    )


class QueueDetailSerializer(serializers.Serializer):
    """
    Detailed queue information serializer.

    Provides comprehensive queue statistics and metadata.
    """

    name = serializers.CharField(help_text="Queue name")
    count = serializers.IntegerField(help_text="Total jobs in queue")

    # Job counts by status
    queued_jobs = serializers.IntegerField(
        default=0, help_text="Jobs waiting to be processed"
    )
    started_jobs = serializers.IntegerField(
        default=0, help_text="Jobs currently being processed"
    )
    finished_jobs = serializers.IntegerField(default=0, help_text="Completed jobs")
    failed_jobs = serializers.IntegerField(default=0, help_text="Failed jobs")
    deferred_jobs = serializers.IntegerField(default=0, help_text="Deferred jobs")
    scheduled_jobs = serializers.IntegerField(default=0, help_text="Scheduled jobs")

    # Worker information
    workers = serializers.IntegerField(
        default=0, help_text="Number of workers for this queue"
    )

    # Metadata
    oldest_job_timestamp = serializers.DateTimeField(
        allow_null=True,
        required=False,
        help_text="Timestamp of oldest job in queue",
    )
    connection_kwargs = serializers.JSONField(
        default=dict, help_text="Redis connection parameters"
    )
    is_async = serializers.BooleanField(default=True, help_text="Queue is in async mode")


class QueueJobListSerializer(serializers.Serializer):
    """
    List of jobs in queue (simple view).
    """

    queue_name = serializers.CharField(help_text="Queue name")
    total_jobs = serializers.IntegerField(help_text="Total number of jobs")
    jobs = serializers.ListField(
        child=serializers.CharField(), default=list, help_text="List of job IDs"
    )
