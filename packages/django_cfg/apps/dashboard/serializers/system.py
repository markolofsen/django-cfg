"""
System Serializers

Serializers for system health and metrics endpoints.
"""

from rest_framework import serializers


class SystemHealthItemSerializer(serializers.Serializer):
    """
    Serializer for system health status items.

    Maps to SystemHealthItem Pydantic model.
    """

    component = serializers.CharField(help_text="Component name")
    status = serializers.ChoiceField(
        choices=['healthy', 'warning', 'error', 'unknown'],
        help_text="Health status"
    )
    description = serializers.CharField(help_text="Status description")
    last_check = serializers.CharField(help_text="Last check time (ISO format)")
    health_percentage = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=100,
        help_text="Health percentage (0-100)"
    )


class SystemHealthSerializer(serializers.Serializer):
    """Serializer for overall system health status."""

    overall_status = serializers.ChoiceField(
        choices=['healthy', 'warning', 'error', 'unknown'],
        help_text="Overall system health status"
    )
    overall_health_percentage = serializers.IntegerField(
        min_value=0,
        max_value=100,
        help_text="Overall health percentage"
    )
    components = SystemHealthItemSerializer(many=True, help_text="Health status of individual components")
    timestamp = serializers.CharField(help_text="Check timestamp (ISO format)")


class SystemMetricsSerializer(serializers.Serializer):
    """Serializer for system performance metrics."""

    cpu_usage = serializers.FloatField(help_text="CPU usage percentage")
    memory_usage = serializers.FloatField(help_text="Memory usage percentage")
    disk_usage = serializers.FloatField(help_text="Disk usage percentage")
    network_in = serializers.CharField(help_text="Network incoming bandwidth")
    network_out = serializers.CharField(help_text="Network outgoing bandwidth")
    response_time = serializers.CharField(help_text="Average response time")
    uptime = serializers.CharField(help_text="System uptime")
