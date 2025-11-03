"""
Charts Serializers

Serializers for chart data endpoints.
"""

from rest_framework import serializers


class ChartDatasetSerializer(serializers.Serializer):
    """Chart.js dataset serializer."""
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.IntegerField())
    backgroundColor = serializers.CharField()
    borderColor = serializers.CharField()
    tension = serializers.FloatField()
    fill = serializers.BooleanField(required=False)


class ChartDataSerializer(serializers.Serializer):
    """Chart.js data structure serializer."""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = ChartDatasetSerializer(many=True)


class ActivityTrackerDaySerializer(serializers.Serializer):
    """Activity tracker single day serializer."""
    date = serializers.DateField()
    count = serializers.IntegerField()
    level = serializers.IntegerField()
    color = serializers.CharField()
    tooltip = serializers.CharField()


class RecentUserSerializer(serializers.Serializer):
    """Recent user serializer."""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    date_joined = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    last_login = serializers.CharField(allow_null=True)
