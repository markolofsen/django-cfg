"""
Requests serializers for gRPC monitoring API.
"""

from rest_framework import serializers


class RecentRequestsSerializer(serializers.Serializer):
    """Recent gRPC requests list."""

    requests = serializers.ListField(
        child=serializers.DictField(), help_text="List of recent requests"
    )
    count = serializers.IntegerField(help_text="Number of requests returned")
    total_available = serializers.IntegerField(help_text="Total requests available")
    offset = serializers.IntegerField(
        default=0, help_text="Current offset for pagination"
    )
    has_more = serializers.BooleanField(
        default=False, help_text="Whether more results are available"
    )


__all__ = ["RecentRequestsSerializer"]
