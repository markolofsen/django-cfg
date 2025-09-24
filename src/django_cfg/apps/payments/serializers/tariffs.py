"""
Tariff serializers.
"""

from rest_framework import serializers
from ..models import Tariff, TariffEndpointGroup


class TariffSerializer(serializers.ModelSerializer):
    """Tariff with pricing info."""
    
    is_free = serializers.SerializerMethodField()
    endpoint_groups_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tariff
        fields = [
            'id', 'name', 'display_name', 'description', 'monthly_price',
            'request_limit', 'is_free', 'is_active', 'endpoint_groups_count'
        ]
    
    def get_is_free(self, obj):
        """Check if tariff is free."""
        return obj.is_free
    
    def get_endpoint_groups_count(self, obj):
        """Get count of enabled endpoint groups."""
        return obj.endpoint_groups.filter(is_enabled=True).count()


class TariffEndpointGroupSerializer(serializers.ModelSerializer):
    """Tariff endpoint group association."""
    
    tariff_name = serializers.CharField(source='tariff.name', read_only=True)
    endpoint_group_name = serializers.CharField(source='endpoint_group.name', read_only=True)
    
    class Meta:
        model = TariffEndpointGroup
        fields = [
            'id', 'tariff', 'tariff_name', 'endpoint_group', 'endpoint_group_name',
            'is_enabled'
        ]


class TariffListSerializer(serializers.ModelSerializer):
    """Simplified tariff for lists."""
    
    is_free = serializers.SerializerMethodField()
    
    class Meta:
        model = Tariff
        fields = ['id', 'name', 'display_name', 'monthly_price', 'is_free', 'is_active']
    
    def get_is_free(self, obj):
        """Check if tariff is free."""
        return obj.is_free
