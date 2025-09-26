"""
Payment Signals for the Universal Payment System v2.0.

Minimal signals focused on cache invalidation and notifications.
Business logic stays in PaymentManager.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone

from ..models import UniversalPayment
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payment_signals")


@receiver(pre_save, sender=UniversalPayment)
def store_original_status(sender, instance: UniversalPayment, **kwargs):
    """Store original status for change detection."""
    if instance.pk:
        try:
            original = UniversalPayment.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except UniversalPayment.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None


@receiver(post_save, sender=UniversalPayment)
def handle_payment_changes(sender, instance: UniversalPayment, created: bool, **kwargs):
    """
    Handle payment changes - only cache clearing and notifications.
    
    Business logic (balance updates, etc.) handled by managers.
    """
    if created:
        logger.info(f"New payment created", extra={
            'payment_id': str(instance.id),
            'user_id': instance.user.id,
            'amount_usd': instance.amount_usd,
            'provider': instance.provider,
            'status': instance.status
        })
    else:
        # Check for status changes
        if hasattr(instance, '_original_status'):
            old_status = instance._original_status
            new_status = instance.status
            
            if old_status != new_status:
                logger.info(f"Payment status changed", extra={
                    'payment_id': str(instance.id),
                    'user_id': instance.user.id,
                    'old_status': old_status,
                    'new_status': new_status
                })
                
                # Handle completed payment
                if new_status == 'completed' and old_status != 'completed':
                    _handle_payment_completed(instance)
                
                # Handle failed payment
                elif new_status in ['failed', 'expired', 'cancelled'] and old_status not in ['failed', 'expired', 'cancelled']:
                    _handle_payment_failed(instance)
    
    # Clear payment-related caches
    _clear_payment_caches(instance)


def _handle_payment_completed(payment: UniversalPayment):
    """
    Handle completed payment - delegate to manager for business logic.
    """
    try:
        # Use manager method which has all the business logic
        from ..models import UserBalance
        
        transaction_record = UserBalance.objects.add_funds_to_user(
            user=payment.user,
            amount=payment.amount_usd,
            transaction_type='payment',
            description=f"Payment completed: {payment.id}",
            payment_id=payment.id
        )
        
        # Mark payment as processed
        payment.completed_at = timezone.now()
        payment.save(update_fields=['completed_at', 'updated_at'])
        
        logger.info(f"Payment completed and processed", extra={
            'payment_id': str(payment.id),
            'user_id': payment.user.id,
            'amount_usd': payment.amount_usd,
            'transaction_id': str(transaction_record.id)
        })
        
    except Exception as e:
        logger.error(f"Failed to process completed payment", extra={
            'payment_id': str(payment.id),
            'user_id': payment.user.id,
            'error': str(e)
        })


def _handle_payment_failed(payment: UniversalPayment):
    """
    Handle failed payment - just logging and notifications.
    """
    try:
        logger.warning(f"Payment failed", extra={
            'payment_id': str(payment.id),
            'user_id': payment.user.id,
            'amount_usd': payment.amount_usd,
            'status': payment.status,
            'provider': payment.provider
        })
        
        # Set failure notification in cache
        cache.set(
            f"payment_failed:{payment.user.id}:{payment.id}",
            {
                'payment_id': str(payment.id),
                'amount_usd': payment.amount_usd,
                'status': payment.status,
                'timestamp': timezone.now().isoformat()
            },
            timeout=86400 * 7  # 7 days
        )
        
    except Exception as e:
        logger.error(f"Failed to handle payment failure", extra={
            'payment_id': str(payment.id),
            'error': str(e)
        })


def _clear_payment_caches(payment: UniversalPayment):
    """Clear payment-related cache entries."""
    try:
        cache_keys = [
            f"user_payments:{payment.user.id}",
            f"payment_stats:{payment.user.id}",
            f"payment_summary:{payment.user.id}",
            f"provider_stats:{payment.provider}",
        ]
        
        cache.delete_many(cache_keys)
        
        logger.debug(f"Cleared payment caches", extra={
            'payment_id': str(payment.id),
            'user_id': payment.user.id,
            'cache_keys_cleared': len(cache_keys)
        })
        
    except Exception as e:
        logger.warning(f"Failed to clear payment caches: {e}")
