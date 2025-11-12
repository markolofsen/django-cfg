"""
DRF serializers for RQ testing and simulation endpoints.
"""

from rest_framework import serializers


class TestScenarioSerializer(serializers.Serializer):
    """Serializer for available test scenarios."""

    id = serializers.CharField(help_text="Scenario ID")
    name = serializers.CharField(help_text="Scenario name")
    description = serializers.CharField(help_text="Scenario description")
    task_func = serializers.CharField(help_text="Task function path")
    default_args = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        default=list,
        help_text="Default arguments (array of any JSON values)"
    )
    default_kwargs = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Default keyword arguments"
    )
    estimated_duration = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Estimated duration in seconds"
    )


class RunDemoRequestSerializer(serializers.Serializer):
    """Serializer for running demo tasks."""

    scenario = serializers.ChoiceField(
        choices=[
            'success',
            'failure',
            'slow',
            'progress',
            'retry',
            'random',
            'memory',
            'cpu',
        ],
        help_text="Demo scenario to run"
    )
    queue = serializers.CharField(
        default='default',
        help_text="Queue name"
    )
    args = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        default=list,
        help_text="Task arguments (array of any JSON values)"
    )
    kwargs = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Task keyword arguments"
    )
    timeout = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Job timeout in seconds"
    )


class StressTestRequestSerializer(serializers.Serializer):
    """Serializer for stress testing."""

    num_jobs = serializers.IntegerField(
        min_value=1,
        max_value=1000,
        default=10,
        help_text="Number of jobs to create"
    )
    queue = serializers.CharField(
        default='default',
        help_text="Queue name"
    )
    scenario = serializers.ChoiceField(
        choices=['success', 'failure', 'slow', 'random'],
        default='success',
        help_text="Task scenario"
    )
    duration = serializers.IntegerField(
        min_value=1,
        max_value=60,
        default=2,
        help_text="Task duration in seconds"
    )


class TestingActionResponseSerializer(serializers.Serializer):
    """Serializer for testing action responses."""

    success = serializers.BooleanField(help_text="Action success status")
    message = serializers.CharField(help_text="Action message")
    job_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Created job IDs"
    )
    count = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="Number of items affected"
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional metadata"
    )


class CleanupRequestSerializer(serializers.Serializer):
    """Serializer for cleanup operations."""

    queue = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Queue name (empty for all queues)"
    )
    registries = serializers.ListField(
        child=serializers.ChoiceField(
            choices=['failed', 'finished', 'deferred', 'scheduled']
        ),
        required=False,
        default=list,
        help_text="Registries to clean"
    )
    delete_demo_jobs_only = serializers.BooleanField(
        default=True,
        help_text="Only delete demo jobs (func starts with 'demo_')"
    )
