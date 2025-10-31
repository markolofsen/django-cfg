"""
Crontab Serializers

Serializers for crontab monitoring endpoints.
"""

from rest_framework import serializers


class CrontabJobSerializer(serializers.Serializer):
    """
    Serializer for individual cron job configuration.

    Maps to CrontabJobConfig Pydantic model.
    """

    name = serializers.CharField(help_text="Job identifier name")
    job_type = serializers.ChoiceField(
        choices=['command', 'callable'],
        help_text="Job type: Django command or Python callable"
    )
    command = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Management command name (for command type jobs)"
    )
    callable_path = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Python callable path (for callable type jobs)"
    )
    command_args = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Command positional arguments"
    )
    command_kwargs = serializers.DictField(
        required=False,
        help_text="Command keyword arguments"
    )
    minute = serializers.CharField(help_text="Cron minute field")
    hour = serializers.CharField(help_text="Cron hour field")
    day_of_month = serializers.CharField(help_text="Cron day of month field")
    month_of_year = serializers.CharField(help_text="Cron month field")
    day_of_week = serializers.CharField(help_text="Cron day of week field")
    enabled = serializers.BooleanField(help_text="Whether job is enabled")
    comment = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Optional job description"
    )
    schedule_display = serializers.CharField(
        required=False,
        help_text="Human-readable schedule description"
    )


class CrontabJobsSerializer(serializers.Serializer):
    """Serializer for list of all cron jobs."""

    enabled = serializers.BooleanField(help_text="Whether crontab is enabled")
    jobs_count = serializers.IntegerField(help_text="Total number of jobs")
    enabled_jobs_count = serializers.IntegerField(help_text="Number of enabled jobs")
    jobs = CrontabJobSerializer(many=True, help_text="List of all cron jobs")


class CrontabStatusSerializer(serializers.Serializer):
    """Serializer for crontab configuration status."""

    enabled = serializers.BooleanField(help_text="Whether crontab is enabled")
    jobs_count = serializers.IntegerField(help_text="Total number of jobs")
    enabled_jobs_count = serializers.IntegerField(help_text="Number of enabled jobs")
    lock_jobs = serializers.BooleanField(help_text="Whether job locking is enabled")
    command_prefix = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Command prefix for all jobs"
    )
    comment = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Crontab configuration comment"
    )
    timestamp = serializers.CharField(help_text="Status check timestamp (ISO format)")
