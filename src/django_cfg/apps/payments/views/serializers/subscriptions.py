"""
Subscription serializers for the Universal Payment System v2.0.

DRF serializers for subscription operations with service integration.
"""

from rest_framework import serializers
from typing import Dict, Any
from django.contrib.auth import get_user_model

from ...models import Subscription, EndpointGroup, Tariff
from ...services import get_subscription_service, SubscriptionCreateRequest, SubscriptionUpdateRequest
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("subscription_serializers")


class EndpointGroupSerializer(serializers.ModelSerializer):
    """
    Endpoint group serializer for API access management.
    
    Used for subscription endpoint group configuration.
    """
    
    class Meta:
        model = EndpointGroup
        fields = [
            'id',
            'name',
            'description',
            'is_enabled',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class TariffSerializer(serializers.ModelSerializer):
    """
    Tariff serializer for subscription pricing.
    
    Used for tariff information and selection.
    """
    
    endpoint_groups = EndpointGroupSerializer(many=True, read_only=True)
    endpoint_groups_count = serializers.IntegerField(source='endpoint_groups.count', read_only=True)
    
    class Meta:
        model = Tariff
        fields = [
            'id',
            'name',
            'description',
            'monthly_price_usd',
            'requests_per_month',
            'requests_per_hour',
            'is_active',
            'endpoint_groups',
            'endpoint_groups_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class SubscriptionListSerializer(serializers.ModelSerializer):
    """
    Lightweight subscription serializer for lists.
    
    Optimized for subscription lists with minimal data.
    """
    
    user = serializers.StringRelatedField(read_only=True)
    tariff_name = serializers.CharField(source='tariff.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id',
            'user',
            'tariff_name',
            'status',
            'status_display',
            'is_active',
            'is_expired',
            'expires_at',
            'created_at',
        ]
        read_only_fields = fields


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Complete subscription serializer with full details.
    
    Used for subscription detail views and updates.
    """
    
    user = serializers.StringRelatedField(read_only=True)
    tariff = TariffSerializer(read_only=True)
    endpoint_group = EndpointGroupSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Only keep fields that actually exist or are needed
    
    class Meta:
        model = Subscription
        fields = [
            'id',
            'user',
            'tariff',
            'endpoint_group',
            'status',
            'status_display',
            'status_color',
            'tier',
            'total_requests',
            'usage_percentage',
            'last_request_at',
            'expires_at',
            'is_active',
            'is_expired',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'total_requests',
            'usage_percentage',
            'last_request_at',
            'created_at',
            'updated_at',
            'status_display',
            'status_color',
            'is_active',
            'is_expired',
        ]


class SubscriptionCreateSerializer(serializers.Serializer):
    """
    Subscription creation serializer with service integration.
    
    Validates input and delegates to SubscriptionService.
    """
    
    tariff_id = serializers.IntegerField(
        min_value=1,
        help_text="Tariff ID for the subscription"
    )
    endpoint_group_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        help_text="Endpoint group ID (optional)"
    )
    duration_days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Subscription duration in days"
    )
    
    def validate_tariff_id(self, value: int) -> int:
        """Validate tariff exists and is active."""
        if not Tariff.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError(f"Tariff {value} not found or inactive")
        return value
    
    def validate_endpoint_group_id(self, value: int) -> int:
        """Validate endpoint group exists and is active."""
        if value and not EndpointGroup.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError(f"Endpoint group {value} not found or inactive")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate subscription creation data."""
        try:
            # Get user from context
            user_id = self.context.get('user_pk') or self.context['request'].user.id
            
            # Create Pydantic request for validation
            request = SubscriptionCreateRequest(
                user_id=user_id,
                **attrs
            )
            
            # Store validated request for create method
            self._validated_request = request
            return attrs
            
        except Exception as e:
            logger.error(f"Subscription validation failed: {e}")
            raise serializers.ValidationError(f"Invalid subscription data: {e}")
    
    def create(self, validated_data: Dict[str, Any]) -> Subscription:
        """Create subscription using SubscriptionService."""
        try:
            subscription_service = get_subscription_service()
            result = subscription_service.create_subscription(self._validated_request)
            
            if result.success:
                # Get the created subscription from database
                subscription = Subscription.objects.get(id=result.subscription_id)
                
                logger.info(f"Subscription created successfully", extra={
                    'subscription_id': result.subscription_id,
                    'user_id': self._validated_request.user_id,
                    'tariff_id': self._validated_request.tariff_id
                })
                
                return subscription
            else:
                logger.error(f"Subscription creation failed: {result.message}")
                raise serializers.ValidationError(result.message)
                
        except Exception as e:
            logger.error(f"Subscription creation error: {e}")
            raise serializers.ValidationError(f"Subscription creation failed: {e}")
    
    def to_representation(self, instance: Subscription) -> Dict[str, Any]:
        """Return full subscription data after creation."""
        return SubscriptionSerializer(instance, context=self.context).data


class SubscriptionUpdateSerializer(serializers.Serializer):
    """
    Subscription update serializer with service integration.
    
    Handles subscription modifications through SubscriptionService.
    """
    
    action = serializers.ChoiceField(
        choices=[
            ('activate', 'Activate'),
            ('suspend', 'Suspend'),
            ('cancel', 'Cancel'),
            ('renew', 'Renew'),
        ],
        help_text="Action to perform on subscription"
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Reason for the action"
    )
    duration_days = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        help_text="Duration for renewal (required for renew action)"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate subscription update data."""
        action = attrs.get('action')
        duration_days = attrs.get('duration_days')
        
        if action == 'renew' and not duration_days:
            raise serializers.ValidationError("duration_days is required for renew action")
        
        return attrs
    
    def save(self) -> Dict[str, Any]:
        """Update subscription using SubscriptionService."""
        try:
            subscription_id = self.context.get('subscription_id')
            if not subscription_id:
                raise serializers.ValidationError("Subscription ID is required")
            
            subscription_service = get_subscription_service()
            action = self.validated_data['action']
            reason = self.validated_data.get('reason')
            duration_days = self.validated_data.get('duration_days')
            
            # Call appropriate service method based on action
            if action == 'activate':
                result = subscription_service.activate_subscription(subscription_id)
            elif action == 'suspend':
                result = subscription_service.suspend_subscription(subscription_id, reason)
            elif action == 'cancel':
                result = subscription_service.cancel_subscription(subscription_id, reason)
            elif action == 'renew':
                result = subscription_service.renew_subscription(subscription_id, duration_days)
            else:
                raise serializers.ValidationError(f"Unknown action: {action}")
            
            if result.success:
                # Get updated subscription
                subscription = Subscription.objects.get(id=result.subscription_id)
                
                return {
                    'success': True,
                    'message': result.message,
                    'subscription': SubscriptionSerializer(subscription, context=self.context).data
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Subscription update error: {e}")
            return {
                'success': False,
                'error': f"Subscription update failed: {e}",
                'error_code': 'subscription_update_error'
            }


class SubscriptionUsageSerializer(serializers.Serializer):
    """
    Subscription usage tracking serializer.
    
    Used for incrementing usage counters.
    """
    
    endpoint = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=200,
        help_text="API endpoint used"
    )
    
    def save(self) -> Dict[str, Any]:
        """Increment subscription usage using SubscriptionService."""
        try:
            subscription_id = self.context.get('subscription_id')
            if not subscription_id:
                raise serializers.ValidationError("Subscription ID is required")
            
            subscription_service = get_subscription_service()
            result = subscription_service.increment_usage(
                subscription_id=subscription_id,
                endpoint=self.validated_data.get('endpoint')
            )
            
            if result.success:
                return {
                    'success': True,
                    'message': result.message,
                    'usage': result.data
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Usage increment error: {e}")
            return {
                'success': False,
                'error': f"Usage increment failed: {e}",
                'error_code': 'usage_increment_error'
            }


class SubscriptionStatsSerializer(serializers.Serializer):
    """
    Subscription statistics serializer.
    
    Used for subscription analytics and reporting.
    """
    
    days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Number of days to analyze"
    )
    
    def save(self) -> Dict[str, Any]:
        """Get subscription statistics using SubscriptionService."""
        try:
            subscription_service = get_subscription_service()
            result = subscription_service.get_subscription_stats(
                days=self.validated_data['days']
            )
            
            if result.success:
                return {
                    'success': True,
                    'stats': result.data,
                    'message': result.message
                }
            else:
                return {
                    'success': False,
                    'error': result.message,
                    'error_code': result.error_code
                }
                
        except Exception as e:
            logger.error(f"Subscription stats error: {e}")
            return {
                'success': False,
                'error': f"Stats generation failed: {e}",
                'error_code': 'stats_error'
            }
