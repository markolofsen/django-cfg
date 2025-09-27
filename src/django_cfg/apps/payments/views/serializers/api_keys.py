"""
API Key serializers for the Universal Payment System v2.0.

DRF serializers for API key operations with service integration.
"""

from rest_framework import serializers
from typing import Dict, Any
from django.contrib.auth import get_user_model

from ...models import APIKey
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("api_key_serializers")


class APIKeyListSerializer(serializers.ModelSerializer):
    """
    Lightweight API key serializer for lists.
    
    Optimized for API key lists with minimal data (no key value).
    """
    
    user = serializers.StringRelatedField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id',
            'user',
            'name',
            'is_active',
            'is_expired',
            'is_valid',
            'total_requests',
            'last_used_at',
            'expires_at',
            'created_at',
        ]
        read_only_fields = fields


class APIKeySerializer(serializers.ModelSerializer):
    """
    Complete API key serializer with full details.
    
    Used for API key detail views (no key value for security).
    """
    
    user = serializers.StringRelatedField(read_only=True)
    key_preview = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id',
            'user',
            'name',
            'key_preview',
            'is_active',
            'is_expired',
            'is_valid',
            'days_until_expiry',
            'total_requests',
            'last_used_at',
            'expires_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'key_preview',
            'is_expired',
            'is_valid',
            'days_until_expiry',
            'total_requests',
            'last_used_at',
            'created_at',
            'updated_at',
        ]


class APIKeyCreateSerializer(serializers.Serializer):
    """
    API key creation serializer with service integration.
    
    Creates new API keys and returns the full key value (only once).
    """
    
    name = serializers.CharField(
        max_length=100,
        help_text="Descriptive name for the API key"
    )
    expires_in_days = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=365,
        help_text="Expiration in days (optional, null for no expiration)"
    )
    
    def validate_name(self, value: str) -> str:
        """Validate API key name is unique for user."""
        user = self.context['request'].user
        user_id = self.context.get('user_pk', user.id)
        
        if APIKey.objects.filter(user_id=user_id, name=value).exists():
            raise serializers.ValidationError(f"API key with name '{value}' already exists")
        
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> APIKey:
        """Create API key using APIKey manager."""
        try:
            user = self.context['request'].user
            user_id = self.context.get('user_pk', user.id)
            
            # Get user object if creating for different user (admin only)
            if str(user_id) != str(user.id):
                if not user.is_staff:
                    raise serializers.ValidationError("Only staff can create API keys for other users")
                user = User.objects.get(id=user_id)
            
            # Create API key using manager
            api_key = APIKey.create_for_user(
                user=user,
                name=validated_data['name'],
                expires_in_days=validated_data.get('expires_in_days')
            )
            
            if api_key:
                logger.info(f"API key created successfully", extra={
                    'api_key_id': str(api_key.id),
                    'user_id': user.id,
                    'name': validated_data['name']
                })
                return api_key
            else:
                raise serializers.ValidationError("Failed to create API key")
                
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User {user_id} not found")
        except Exception as e:
            logger.error(f"API key creation error: {e}")
            raise serializers.ValidationError(f"API key creation failed: {e}")
    
    def to_representation(self, instance: APIKey) -> Dict[str, Any]:
        """Return API key data with full key value (only on creation)."""
        data = APIKeySerializer(instance, context=self.context).data
        
        # Add full key value only on creation (security: shown only once)
        data['key'] = instance.key
        data['warning'] = "This is the only time the full API key will be shown. Please save it securely."
        
        return data


class APIKeyUpdateSerializer(serializers.ModelSerializer):
    """
    API key update serializer for modifying API key properties.
    
    Allows updating name and active status only.
    """
    
    class Meta:
        model = APIKey
        fields = ['name', 'is_active']
    
    def validate_name(self, value: str) -> str:
        """Validate API key name is unique for user."""
        user_id = self.instance.user_id
        
        # Check if another API key with same name exists for this user
        existing = APIKey.objects.filter(
            user_id=user_id,
            name=value
        ).exclude(id=self.instance.id)
        
        if existing.exists():
            raise serializers.ValidationError(f"API key with name '{value}' already exists")
        
        return value
    
    def update(self, instance: APIKey, validated_data: Dict[str, Any]) -> APIKey:
        """Update API key with logging."""
        old_name = instance.name
        old_active = instance.is_active
        
        instance = super().update(instance, validated_data)
        
        # Log changes
        changes = []
        if instance.name != old_name:
            changes.append(f"name: {old_name} → {instance.name}")
        if instance.is_active != old_active:
            changes.append(f"active: {old_active} → {instance.is_active}")
        
        if changes:
            logger.info(f"API key updated: {', '.join(changes)}", extra={
                'api_key_id': str(instance.id),
                'user_id': instance.user_id
            })
        
        return instance


class APIKeyActionSerializer(serializers.Serializer):
    """
    API key action serializer for key operations.
    
    Handles deactivation, extension, and usage increment.
    """
    
    action = serializers.ChoiceField(
        choices=[
            ('deactivate', 'Deactivate'),
            ('extend', 'Extend Expiration'),
            ('increment_usage', 'Increment Usage'),
        ],
        help_text="Action to perform on API key"
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Reason for deactivation"
    )
    days = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=365,
        help_text="Days to extend expiration"
    )
    ip_address = serializers.IPAddressField(
        required=False,
        allow_null=True,
        help_text="IP address for usage tracking"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate action-specific requirements."""
        action = attrs.get('action')
        
        if action == 'extend' and not attrs.get('days'):
            raise serializers.ValidationError("days is required for extend action")
        
        return attrs
    
    def save(self) -> Dict[str, Any]:
        """Perform API key action."""
        try:
            api_key_id = self.context.get('api_key_id')
            if not api_key_id:
                raise serializers.ValidationError("API key ID is required")
            
            api_key = APIKey.objects.get(id=api_key_id)
            action = self.validated_data['action']
            
            if action == 'deactivate':
                reason = self.validated_data.get('reason')
                success = api_key.deactivate(reason=reason)
                message = f"API key deactivated successfully"
                
            elif action == 'extend':
                days = self.validated_data['days']
                success = api_key.extend_expiry(days=days)
                message = f"API key expiration extended by {days} days"
                
            elif action == 'increment_usage':
                ip_address = self.validated_data.get('ip_address')
                success = api_key.increment_usage(ip_address=ip_address)
                message = f"API key usage incremented"
                
            else:
                raise serializers.ValidationError(f"Unknown action: {action}")
            
            if success:
                # Refresh from database
                api_key.refresh_from_db()
                
                return {
                    'success': True,
                    'message': message,
                    'api_key': APIKeySerializer(api_key, context=self.context).data
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to {action} API key",
                    'error_code': f'{action}_failed'
                }
                
        except APIKey.DoesNotExist:
            return {
                'success': False,
                'error': 'API key not found',
                'error_code': 'api_key_not_found'
            }
        except Exception as e:
            logger.error(f"API key action error: {e}")
            return {
                'success': False,
                'error': f"API key action failed: {e}",
                'error_code': 'api_key_action_error'
            }


class APIKeyValidationSerializer(serializers.Serializer):
    """
    API key validation serializer.
    
    Validates API key and returns key information.
    """
    
    key = serializers.CharField(
        min_length=32,
        max_length=64,
        help_text="API key to validate"
    )
    
    def validate_key(self, value: str) -> str:
        """Validate API key format."""
        if not value.startswith('pk_'):
            raise serializers.ValidationError("Invalid API key format")
        return value
    
    def save(self) -> Dict[str, Any]:
        """Validate API key and return information."""
        try:
            key_value = self.validated_data['key']
            api_key = APIKey.get_valid_key(key_value)
            
            if api_key:
                return {
                    'success': True,
                    'valid': True,
                    'api_key': APIKeySerializer(api_key, context=self.context).data,
                    'message': 'API key is valid'
                }
            else:
                return {
                    'success': True,
                    'valid': False,
                    'api_key': None,
                    'message': 'API key is invalid or expired'
                }
                
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return {
                'success': False,
                'error': f"API key validation failed: {e}",
                'error_code': 'validation_error'
            }


class APIKeyValidationResponseSerializer(serializers.Serializer):
    """
    API key validation response serializer.
    
    Defines the structure of API key validation response for OpenAPI schema.
    """
    success = serializers.BooleanField(help_text="Whether the validation was successful")
    valid = serializers.BooleanField(help_text="Whether the API key is valid")
    api_key = APIKeySerializer(allow_null=True, help_text="API key details if valid")
    message = serializers.CharField(help_text="Validation message")
    error = serializers.CharField(required=False, help_text="Error message if validation failed")
    error_code = serializers.CharField(required=False, help_text="Error code if validation failed")


class APIKeyStatsSerializer(serializers.Serializer):
    """
    API key statistics serializer.
    
    Used for API key analytics and reporting.
    """
    
    days = serializers.IntegerField(
        default=30,
        min_value=1,
        max_value=365,
        help_text="Number of days to analyze"
    )
    
    def save(self) -> Dict[str, Any]:
        """Get API key statistics."""
        try:
            from django.db import models
            from django.utils import timezone
            from datetime import timedelta
            
            days = self.validated_data['days']
            since_date = timezone.now() - timedelta(days=days)
            
            # Get user-specific stats if user context provided
            user_id = self.context.get('user_pk')
            if user_id:
                queryset = APIKey.objects.filter(user_id=user_id)
            else:
                queryset = APIKey.objects.all()
            
            stats = queryset.aggregate(
                total_keys=models.Count('id'),
                active_keys=models.Count('id', filter=models.Q(is_active=True)),
                expired_keys=models.Count('id', filter=models.Q(expires_at__lt=timezone.now())),
                total_requests=models.Sum('total_requests'),
                recent_usage=models.Count(
                    'id',
                    filter=models.Q(last_used_at__gte=since_date)
                ),
            )
            
            return {
                'success': True,
                'stats': {
                    **stats,
                    'total_requests': stats['total_requests'] or 0,
                    'inactive_keys': stats['total_keys'] - stats['active_keys'],
                    'usage_rate': (stats['recent_usage'] / stats['total_keys'] * 100) if stats['total_keys'] > 0 else 0,
                },
                'period_days': days,
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"API key stats error: {e}")
            return {
                'success': False,
                'error': f"Stats generation failed: {e}",
                'error_code': 'stats_error'
            }
