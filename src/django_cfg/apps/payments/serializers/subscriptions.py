"""
Subscription serializers.
"""

from rest_framework import serializers
from ..models import Subscription, EndpointGroup


class EndpointGroupSerializer(serializers.ModelSerializer):
    """Endpoint group with pricing tiers."""
    
    class Meta:
        model = EndpointGroup
        fields = [
            'id', 'name', 'display_name', 'description',
            'basic_price', 'premium_price', 'enterprise_price',
            'basic_limit', 'premium_limit', 'enterprise_limit',
            'is_active', 'require_api_key'
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription with computed fields."""
    
    endpoint_group_name = serializers.CharField(source='endpoint_group.name', read_only=True)
    endpoint_group_display = serializers.CharField(source='endpoint_group.display_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    is_active_subscription = serializers.ReadOnlyField(source='is_active')
    is_usage_exceeded = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'endpoint_group', 'endpoint_group_name', 'endpoint_group_display',
            'tier', 'tier_display', 'status', 'status_display', 'monthly_price',
            'usage_limit', 'usage_current', 'is_active_subscription', 'is_usage_exceeded',
            'last_billed', 'next_billing', 'expires_at', 'created_at'
        ]
        read_only_fields = [
            'usage_current', 'last_billed', 'next_billing', 'cancelled_at', 'created_at'
        ]


class SubscriptionCreateSerializer(serializers.Serializer):
    """Create subscription request."""
    
    endpoint_group_id = serializers.IntegerField()
    tier = serializers.ChoiceField(choices=Subscription.SubscriptionTier.choices)
    
    def validate_endpoint_group_id(self, value):
        """Validate endpoint group exists."""
        try:
            endpoint_group = EndpointGroup.objects.get(id=value, is_active=True)
            return value
        except EndpointGroup.DoesNotExist:
            raise serializers.ValidationError("Endpoint group not found or inactive")


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Simplified subscription for lists."""
    
    endpoint_group_name = serializers.CharField(source='endpoint_group.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'endpoint_group_name', 'tier', 'status', 'status_display',
            'monthly_price', 'usage_current', 'usage_limit', 'expires_at'
        ]
