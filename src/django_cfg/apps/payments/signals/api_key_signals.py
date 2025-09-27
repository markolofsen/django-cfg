"""
API Key Signals for the Universal Payment System v2.0.

Minimal signals focused on cache invalidation and security notifications.
Business logic stays in APIKeyManager.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone

from ..models import APIKey
from django_cfg.modules.django_logger import get_logger

logger = get_logger("api_key_signals")


@receiver(pre_save, sender=APIKey)
def store_original_api_key_data(sender, instance: APIKey, **kwargs):
    """Store original API key data for change detection."""
    if instance.pk:
        try:
            original = APIKey.objects.get(pk=instance.pk)
            instance._original_is_active = original.is_active
            instance._original_total_requests = original.total_requests
        except APIKey.DoesNotExist:
            instance._original_is_active = None
            instance._original_total_requests = None
    else:
        instance._original_is_active = None
        instance._original_total_requests = None


@receiver(post_save, sender=APIKey)
def handle_api_key_changes(sender, instance: APIKey, created: bool, **kwargs):
    """
    Handle API key changes - only cache clearing and security notifications.
    
    Business logic (usage tracking, validation) stays in managers.
    """
    if created:
        logger.info(f"New API key created", extra={
            'api_key_id': str(instance.id),
            'user_id': instance.user.id,
            'key_name': instance.name,
            'expires_at': instance.expires_at.isoformat() if instance.expires_at else None
        })
        
        # Set creation notification in cache
        cache.set(
            f"api_key_created:{instance.user.id}:{instance.id}",
            {
                'api_key_id': str(instance.id),
                'key_name': instance.name,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400  # 24 hours
        )
        
    else:
        # Check for status changes
        if hasattr(instance, '_original_is_active'):
            old_active = instance._original_is_active
            new_active = instance.is_active
            
            if old_active != new_active:
                if new_active:
                    _handle_api_key_activated(instance)
                else:
                    _handle_api_key_deactivated(instance)
        
        # Check for usage increases (security monitoring)
        if hasattr(instance, '_original_total_requests'):
            old_requests = instance._original_total_requests or 0
            new_requests = instance.total_requests
            
            if new_requests > old_requests:
                request_increase = new_requests - old_requests
                
                # Log high usage increases (potential security concern)
                if request_increase > 100:  # More than 100 requests at once
                    logger.warning(f"High API key usage increase", extra={
                        'api_key_id': str(instance.id),
                        'user_id': instance.user.id,
                        'old_requests': old_requests,
                        'new_requests': new_requests,
                        'increase': request_increase
                    })
                    
                    _handle_high_usage_alert(instance, request_increase)
    
    # Clear API key-related caches
    _clear_api_key_caches(instance)


@receiver(post_delete, sender=APIKey)
def handle_api_key_deletion(sender, instance: APIKey, **kwargs):
    """Handle API key deletion."""
    logger.warning(f"API key deleted", extra={
        'api_key_id': str(instance.id),
        'user_id': instance.user.id,
        'name': instance.name,
        'total_requests': instance.total_requests,
        'deletion_timestamp': timezone.now().isoformat()
    })
    
    # Set deletion notification in cache
    cache.set(
        f"api_key_deleted:{instance.user.id}:{instance.id}",
        {
            'api_key_id': str(instance.id),
            'name': instance.name,
            'total_requests': instance.total_requests,
            'timestamp': timezone.now().isoformat()
        },
        timeout=86400 * 30  # 30 days for audit
    )
    
    # Clear caches
    _clear_api_key_caches(instance)


# Helper functions (notifications and security monitoring only)

def _handle_api_key_activated(api_key: APIKey):
    """Handle API key activation (notification only)."""
    try:
        logger.info(f"API key activated", extra={
            'api_key_id': str(api_key.id),
            'user_id': api_key.user.id,
            'name': api_key.name
        })
        
        # Set activation notification in cache
        cache.set(
            f"api_key_activated:{api_key.user.id}:{api_key.id}",
            {
                'api_key_id': str(api_key.id),
                'name': api_key.name,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400  # 24 hours
        )
        
    except Exception as e:
        logger.error(f"Failed to handle API key activation: {e}")


def _handle_api_key_deactivated(api_key: APIKey):
    """Handle API key deactivation (security notification)."""
    try:
        logger.warning(f"API key deactivated", extra={
            'api_key_id': str(api_key.id),
            'user_id': api_key.user.id,
            'name': api_key.name,
            'total_requests': api_key.total_requests
        })
        
        # Set deactivation notification in cache
        cache.set(
            f"api_key_deactivated:{api_key.user.id}:{api_key.id}",
            {
                'api_key_id': str(api_key.id),
                'name': api_key.name,
                'total_requests': api_key.total_requests,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400 * 7  # 7 days
        )
        
    except Exception as e:
        logger.error(f"Failed to handle API key deactivation: {e}")


def _handle_high_usage_alert(api_key: APIKey, request_increase: int):
    """Handle high usage alert (security monitoring)."""
    try:
        logger.warning(f"High API key usage detected", extra={
            'api_key_id': str(api_key.id),
            'user_id': api_key.user.id,
            'request_increase': request_increase,
            'total_requests': api_key.total_requests
        })
        
        # Set high usage alert in cache
        cache.set(
            f"high_usage_alert:{api_key.user.id}:{api_key.id}",
            {
                'api_key_id': str(api_key.id),
                'request_increase': request_increase,
                'total_requests': api_key.total_requests,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400  # 24 hours
        )
        
        # Check if we should temporarily disable the key (security measure)
        if request_increase > 1000:  # More than 1000 requests at once
            logger.critical(f"Extremely high API usage - potential abuse", extra={
                'api_key_id': str(api_key.id),
                'user_id': api_key.user.id,
                'request_increase': request_increase
            })
            
            # Set critical alert flag
            cache.set(
                f"critical_usage_alert:{api_key.user.id}:{api_key.id}",
                {
                    'api_key_id': str(api_key.id),
                    'request_increase': request_increase,
                    'timestamp': timezone.now().isoformat(),
                    'action_required': True
                },
                timeout=86400 * 7  # 7 days
            )
        
    except Exception as e:
        logger.error(f"Failed to handle high usage alert: {e}")


def _clear_api_key_caches(api_key: APIKey):
    """Clear API key-related cache entries."""
    try:
        cache_keys = [
            f"api_key_validation:{api_key.key[:10]}...",  # Partial key for security
            f"user_api_keys:{api_key.user.id}",
            f"api_key_stats:{api_key.user.id}",
            f"api_key_usage:{api_key.id}",
        ]
        
        cache.delete_many(cache_keys)
        
        logger.debug(f"Cleared API key caches", extra={
            'api_key_id': str(api_key.id),
            'user_id': api_key.user.id,
            'cache_keys_cleared': len(cache_keys)
        })
        
    except Exception as e:
        logger.warning(f"Failed to clear API key caches: {e}")
