"""
Subscription Signals for the Universal Payment System v2.0.

Minimal signals focused on cache invalidation and notifications.
Business logic stays in SubscriptionManager.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone

from ..models import Subscription
from django_cfg.modules.django_logger import get_logger

logger = get_logger("subscription_signals")


@receiver(pre_save, sender=Subscription)
def store_original_subscription_data(sender, instance: Subscription, **kwargs):
    """Store original subscription data for change detection."""
    if instance.pk:
        try:
            original = Subscription.objects.get(pk=instance.pk)
            instance._original_status = original.status
            instance._original_tier = original.tier
            instance._original_expires_at = original.expires_at
        except Subscription.DoesNotExist:
            instance._original_status = None
            instance._original_tier = None
            instance._original_expires_at = None
    else:
        instance._original_status = None
        instance._original_tier = None
        instance._original_expires_at = None


@receiver(post_save, sender=Subscription)
def handle_subscription_changes(sender, instance: Subscription, created: bool, **kwargs):
    """
    Handle subscription changes - only cache clearing and notifications.
    
    Business logic (API key management, etc.) stays in managers.
    """
    if created:
        logger.info(f"New subscription created", extra={
            'subscription_id': str(instance.id),
            'user_id': instance.user.id,
            'tier': instance.tier,
            'status': instance.status
        })
        
        # Create default API key for new subscription (delegate to manager)
        _create_default_api_key(instance)
        
    else:
        # Check for status changes
        if hasattr(instance, '_original_status'):
            old_status = instance._original_status
            new_status = instance.status
            
            if old_status != new_status:
                logger.info(f"Subscription status changed", extra={
                    'subscription_id': str(instance.id),
                    'user_id': instance.user.id,
                    'old_status': old_status,
                    'new_status': new_status
                })
                
                # Handle activation
                if new_status == 'active' and old_status != 'active':
                    _handle_subscription_activated(instance)
                
                # Handle suspension/cancellation
                elif new_status in ['suspended', 'cancelled'] and old_status not in ['suspended', 'cancelled']:
                    _handle_subscription_deactivated(instance)
        
        # Check for tier changes
        if hasattr(instance, '_original_tier'):
            old_tier = instance._original_tier
            new_tier = instance.tier
            
            if old_tier != new_tier:
                logger.info(f"Subscription tier changed", extra={
                    'subscription_id': str(instance.id),
                    'user_id': instance.user.id,
                    'old_tier': old_tier,
                    'new_tier': new_tier
                })
                
                _handle_tier_change(instance, old_tier, new_tier)
        
        # Check for expiration changes
        if hasattr(instance, '_original_expires_at'):
            old_expires = instance._original_expires_at
            new_expires = instance.expires_at
            
            if old_expires != new_expires:
                logger.info(f"Subscription expiration changed", extra={
                    'subscription_id': str(instance.id),
                    'user_id': instance.user.id,
                    'old_expires': old_expires.isoformat() if old_expires else None,
                    'new_expires': new_expires.isoformat() if new_expires else None
                })
    
    # Clear subscription-related caches
    _clear_subscription_caches(instance)


@receiver(post_delete, sender=Subscription)
def handle_subscription_deletion(sender, instance: Subscription, **kwargs):
    """Handle subscription deletion."""
    logger.warning(f"Subscription deleted", extra={
        'subscription_id': str(instance.id),
        'user_id': instance.user.id,
        'tier': instance.tier,
        'status': instance.status,
        'deletion_timestamp': timezone.now().isoformat()
    })
    
    # Clear caches
    _clear_subscription_caches(instance)


# Helper functions (notifications and delegations only)

def _create_default_api_key(subscription: Subscription):
    """Create default API key for new subscription (delegate to manager)."""
    try:
        from ..models import APIKey
        
        # Use manager method which has all the business logic
        api_key = APIKey.objects.create_api_key_for_user(
            user=subscription.user,
            name=f"Default API Key ({subscription.tier})",
            expires_in_days=None  # No expiration for default key
        )
        
        logger.info(f"Created default API key for subscription", extra={
            'subscription_id': str(subscription.id),
            'user_id': subscription.user.id,
            'api_key_id': str(api_key.id)
        })
        
    except Exception as e:
        logger.error(f"Failed to create default API key", extra={
            'subscription_id': str(subscription.id),
            'user_id': subscription.user.id,
            'error': str(e)
        })


def _handle_subscription_activated(subscription: Subscription):
    """Handle subscription activation (notification only)."""
    try:
        logger.info(f"Subscription activated", extra={
            'subscription_id': str(subscription.id),
            'user_id': subscription.user.id,
            'tier': subscription.tier
        })
        
        # Set activation notification in cache
        cache.set(
            f"subscription_activated:{subscription.user.id}",
            {
                'subscription_id': str(subscription.id),
                'tier': subscription.tier,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400  # 24 hours
        )
        
    except Exception as e:
        logger.error(f"Failed to handle subscription activation: {e}")


def _handle_subscription_deactivated(subscription: Subscription):
    """Handle subscription deactivation (notification only)."""
    try:
        logger.warning(f"Subscription deactivated", extra={
            'subscription_id': str(subscription.id),
            'user_id': subscription.user.id,
            'status': subscription.status,
            'tier': subscription.tier
        })
        
        # Set deactivation notification in cache
        cache.set(
            f"subscription_deactivated:{subscription.user.id}",
            {
                'subscription_id': str(subscription.id),
                'status': subscription.status,
                'tier': subscription.tier,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400 * 7  # 7 days
        )
        
    except Exception as e:
        logger.error(f"Failed to handle subscription deactivation: {e}")


def _handle_tier_change(subscription: Subscription, old_tier: str, new_tier: str):
    """Handle subscription tier change (notification only)."""
    try:
        logger.info(f"Subscription tier changed", extra={
            'subscription_id': str(subscription.id),
            'user_id': subscription.user.id,
            'old_tier': old_tier,
            'new_tier': new_tier
        })
        
        # Set tier change notification in cache
        cache.set(
            f"tier_changed:{subscription.user.id}",
            {
                'subscription_id': str(subscription.id),
                'old_tier': old_tier,
                'new_tier': new_tier,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400  # 24 hours
        )
        
    except Exception as e:
        logger.error(f"Failed to handle tier change: {e}")


def _clear_subscription_caches(subscription: Subscription):
    """Clear subscription-related cache entries."""
    try:
        cache_keys = [
            f"user_subscription:{subscription.user.id}",
            f"subscription_access:{subscription.user.id}",
            f"subscription_stats:{subscription.user.id}",
            f"tier_limits:{subscription.tier}",
        ]
        
        cache.delete_many(cache_keys)
        
        logger.debug(f"Cleared subscription caches", extra={
            'subscription_id': str(subscription.id),
            'user_id': subscription.user.id,
            'cache_keys_cleared': len(cache_keys)
        })
        
    except Exception as e:
        logger.warning(f"Failed to clear subscription caches: {e}")
