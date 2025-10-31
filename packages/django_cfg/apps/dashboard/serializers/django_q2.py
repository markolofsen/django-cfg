"""
Django-Q2 Task Serializers

Serializers for displaying Django-Q2 scheduled tasks and task history.
"""

from rest_framework import serializers


class DjangoQ2ScheduleSerializer(serializers.Serializer):
    """Serializer for Django-Q2 scheduled tasks."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    func = serializers.CharField(max_length=512)
    schedule_type = serializers.CharField(max_length=24)
    repeats = serializers.IntegerField()
    next_run = serializers.DateTimeField(allow_null=True)
    last_run = serializers.DateTimeField(allow_null=True)


class DjangoQ2TaskSerializer(serializers.Serializer):
    """Serializer for Django-Q2 task execution history."""

    id = serializers.CharField(max_length=32)
    name = serializers.CharField(max_length=255)
    func = serializers.CharField(max_length=512)
    started = serializers.DateTimeField()
    stopped = serializers.DateTimeField(allow_null=True)
    success = serializers.BooleanField()
    result = serializers.CharField(allow_null=True)


class DjangoQ2StatusSerializer(serializers.Serializer):
    """Serializer for Django-Q2 cluster status."""

    cluster_running = serializers.BooleanField()
    total_schedules = serializers.IntegerField()
    active_schedules = serializers.IntegerField()
    recent_tasks = serializers.IntegerField()
    successful_tasks = serializers.IntegerField()
    failed_tasks = serializers.IntegerField()


class DjangoQ2SummarySerializer(serializers.Serializer):
    """Summary serializer for Django-Q2 dashboard."""

    status = DjangoQ2StatusSerializer()
    schedules = DjangoQ2ScheduleSerializer(many=True)
    recent_tasks = DjangoQ2TaskSerializer(many=True)
