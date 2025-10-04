"""
Serializers for Django CFG Tasks app.

Provides DRF serializers for task management API endpoints.
"""

from rest_framework import serializers
from typing import Dict, Any


class QueueStatusSerializer(serializers.Serializer):
    """Serializer for queue status data."""
    
    queues = serializers.DictField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        help_text="Queue information with pending/failed counts"
    )
    workers = serializers.IntegerField(help_text="Number of active workers")
    redis_connected = serializers.BooleanField(help_text="Redis connection status")
    timestamp = serializers.CharField(help_text="Current timestamp")
    error = serializers.CharField(required=False, help_text="Error message if any")


class TaskStatisticsSerializer(serializers.Serializer):
    """Serializer for task statistics data."""
    
    statistics = serializers.DictField(
        child=serializers.IntegerField(),
        help_text="Task count statistics"
    )
    recent_tasks = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of recent tasks"
    )
    timestamp = serializers.CharField(help_text="Current timestamp")
    error = serializers.CharField(required=False, help_text="Error message if any")


class WorkerActionSerializer(serializers.Serializer):
    """Serializer for worker management actions."""
    
    action = serializers.ChoiceField(
        choices=['start', 'stop', 'restart'],
        help_text="Action to perform on workers"
    )
    processes = serializers.IntegerField(
        default=1,
        min_value=1,
        max_value=10,
        help_text="Number of worker processes"
    )
    threads = serializers.IntegerField(
        default=2,
        min_value=1,
        max_value=20,
        help_text="Number of threads per process"
    )


class QueueActionSerializer(serializers.Serializer):
    """Serializer for queue management actions."""
    
    action = serializers.ChoiceField(
        choices=['clear', 'clear_all', 'purge', 'purge_failed', 'flush'],
        help_text="Action to perform on queues"
    )
    queue_names = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Specific queues to target (empty = all queues)"
    )


class APIResponseSerializer(serializers.Serializer):
    """Standard API response serializer."""
    
    success = serializers.BooleanField(help_text="Operation success status")
    message = serializers.CharField(required=False, help_text="Success message")
    error = serializers.CharField(required=False, help_text="Error message")
    data = serializers.DictField(required=False, help_text="Response data")
