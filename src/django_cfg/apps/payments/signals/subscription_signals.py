"""
🔄 Universal Subscription Signals

Automatic subscription management and lifecycle handling via Django signals.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django_cfg.modules.django_logger import get_logger

from ..models import Subscription, EndpointGroup, UserBalance, Transaction
from ..services.cache import SimpleCache

logger = get_logger("subscription_signals")


@receiver(pre_save, sender=Subscription)
def store_original_subscription_status(sender, instance, **kwargs):
    """Store original subscription status for change detection."""
    if instance.pk:
        try:
            old_instance = Subscription.objects.get(pk=instance.pk)
            instance._original_status = old_instance.status
            instance._original_expires_at = old_instance.expires_at
        except Subscription.DoesNotExist:
            instance._original_status = None
            instance._original_expires_at = None


@receiver(post_save, sender=Subscription)
def process_subscription_status_changes(sender, instance, created, **kwargs):
    """Process subscription status changes and handle lifecycle events."""
    if created:
        logger.info(
            f"New subscription created: {instance.endpoint_group.name} "
            f"for user {instance.user.email} (expires: {instance.expires_at})"
        )
        _clear_user_cache(instance.user.id)
        return
    
    # Check if status changed
    if hasattr(instance, '_original_status'):
        old_status = instance._original_status
        new_status = instance.status
        
        if old_status != new_status:
            logger.info(
                f"Subscription status changed: {instance.endpoint_group.name} "
                f"for user {instance.user.email} - {old_status} → {new_status}"
            )
            
            # Handle specific status changes
            if new_status == Subscription.SubscriptionStatus.ACTIVE:
                _handle_subscription_activation(instance)
            elif new_status == Subscription.SubscriptionStatus.CANCELLED:
                _handle_subscription_cancellation(instance)
            elif new_status == Subscription.SubscriptionStatus.EXPIRED:
                _handle_subscription_expiration(instance)
            
            _clear_user_cache(instance.user.id)


@receiver(post_save, sender=Subscription)
def handle_subscription_renewal(sender, instance, created, **kwargs):
    """Handle subscription renewal and billing."""
    if created or not hasattr(instance, '_original_expires_at'):
        return
    
    old_expires_at = instance._original_expires_at
    new_expires_at = instance.expires_at
    
    # Check if subscription was renewed (expires_at extended)
    if old_expires_at and new_expires_at and new_expires_at > old_expires_at:
        logger.info(
            f"Subscription renewed: {instance.endpoint_group.name} "
            f"for user {instance.user.email} - extended to {new_expires_at}"
        )
        _clear_user_cache(instance.user.id)


@receiver(post_delete, sender=Subscription)
def log_subscription_deletion(sender, instance, **kwargs):
    """Log subscription deletions for audit purposes."""
    logger.warning(
        f"Subscription deleted: {instance.endpoint_group.name} "
        f"for user {instance.user.email} - Status was: {instance.status}"
    )
    _clear_user_cache(instance.user.id)


@receiver(post_save, sender=EndpointGroup)
def log_endpoint_group_changes(sender, instance, created, **kwargs):
    """Log endpoint group changes that may affect subscriptions."""
    if created:
        logger.info(f"New endpoint group created: {instance.name}")
    else:
        # Check if important fields changed
        if instance.tracker.has_changed('is_active'):
            logger.warning(
                f"Endpoint group activity changed: {instance.name} "
                f"- active: {instance.is_active}"
            )
            # Clear cache for all users with subscriptions to this group
            _clear_endpoint_group_cache(instance)


def _handle_subscription_activation(subscription: Subscription):
    """Handle subscription activation logic."""
    try:
        # Reset usage counters
        subscription.usage_current = 0
        
        # Set next billing date
        if not subscription.next_billing:
            subscription.next_billing = timezone.now() + timedelta(days=30)  # Monthly by default
        
        subscription.save(update_fields=['usage_current', 'next_billing'])
        
        logger.info(f"Subscription activated: {subscription.endpoint_group.name} for {subscription.user.email}")
        
    except Exception as e:
        logger.error(f"Error handling subscription activation: {e}")


def _handle_subscription_cancellation(subscription: Subscription):
    """Handle subscription cancellation logic."""
    try:
        # Mark as cancelled
        subscription.cancelled_at = timezone.now()
        subscription.save(update_fields=['cancelled_at'])
        
        logger.info(f"Subscription cancelled: {subscription.endpoint_group.name} for {subscription.user.email}")
        
    except Exception as e:
        logger.error(f"Error handling subscription cancellation: {e}")


def _handle_subscription_expiration(subscription: Subscription):
    """Handle subscription expiration logic."""
    try:
        # Mark as expired
        subscription.expired_at = timezone.now()
        subscription.save(update_fields=['expired_at'])
        
        logger.info(f"Subscription expired: {subscription.endpoint_group.name} for {subscription.user.email}")
        
    except Exception as e:
        logger.error(f"Error handling subscription expiration: {e}")


def _clear_user_cache(user_id: int):
    """Clear cache for specific user."""
    try:
        cache = SimpleCache("subscriptions")
        cache_keys = [
            f"access:{user_id}",
            f"subscriptions:{user_id}",
            f"user_summary:{user_id}",
        ]
        
        for key in cache_keys:
            cache.delete(key)
            
    except Exception as e:
        logger.warning(f"Failed to clear cache for user {user_id}: {e}")


def _clear_endpoint_group_cache(endpoint_group: EndpointGroup):
    """Clear cache for all users with subscriptions to this endpoint group."""
    try:
        # Get all users with active subscriptions to this group
        user_ids = Subscription.objects.filter(
            endpoint_group=endpoint_group,
            status=Subscription.SubscriptionStatus.ACTIVE
        ).values_list('user_id', flat=True)
        
        for user_id in user_ids:
            _clear_user_cache(user_id)
            
    except Exception as e:
        logger.warning(f"Failed to clear cache for endpoint group {endpoint_group.name}: {e}")


@receiver(post_save, sender=Subscription)
def update_usage_statistics(sender, instance, created, **kwargs):
    """Update usage statistics when subscription is modified."""
    if not created and hasattr(instance, '_original_status'):
        # Only update stats if usage-related fields might have changed
        if instance.usage_current != getattr(instance, '_original_usage_current', instance.usage_current):
            logger.debug(
                f"Usage updated for subscription {instance.endpoint_group.name}: "
                f"{instance.usage_current} requests"
            )
