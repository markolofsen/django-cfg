"""
Worker information serializers for Django-RQ.
"""

from rest_framework import serializers


class WorkerSerializer(serializers.Serializer):
    """
    Worker information serializer.

    Provides detailed information about an RQ worker.
    """

    name = serializers.CharField(help_text="Worker name/ID")
    queues = serializers.ListField(
        child=serializers.CharField(), default=list, help_text="List of queue names"
    )
    state = serializers.CharField(help_text="Worker state (idle/busy/suspended)")
    current_job = serializers.CharField(
        allow_null=True, required=False, help_text="Current job ID if busy"
    )
    birth = serializers.DateTimeField(help_text="Worker start time")
    last_heartbeat = serializers.DateTimeField(help_text="Last heartbeat timestamp")
    successful_job_count = serializers.IntegerField(
        default=0, help_text="Total successful jobs"
    )
    failed_job_count = serializers.IntegerField(default=0, help_text="Total failed jobs")
    total_working_time = serializers.FloatField(
        default=0.0, help_text="Total working time in seconds"
    )


class WorkerStatsSerializer(serializers.Serializer):
    """
    Aggregated worker statistics serializer.

    Provides overview of all workers across all queues.
    """

    total_workers = serializers.IntegerField(help_text="Total number of workers")
    busy_workers = serializers.IntegerField(default=0, help_text="Number of busy workers")
    idle_workers = serializers.IntegerField(default=0, help_text="Number of idle workers")
    suspended_workers = serializers.IntegerField(
        default=0, help_text="Number of suspended workers"
    )
    total_successful_jobs = serializers.IntegerField(
        default=0, help_text="Total successful jobs (all workers)"
    )
    total_failed_jobs = serializers.IntegerField(
        default=0, help_text="Total failed jobs (all workers)"
    )
    total_working_time = serializers.FloatField(
        default=0.0, help_text="Total working time across all workers (seconds)"
    )
    workers = serializers.ListField(
        child=WorkerSerializer(), default=list, help_text="List of individual workers"
    )
