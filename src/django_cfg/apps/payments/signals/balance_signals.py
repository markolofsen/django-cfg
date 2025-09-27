"""
Balance Signals for the Universal Payment System v2.0.

Minimal signals focused on cache invalidation and notifications.
Business logic stays in UserBalanceManager and TransactionManager.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal

from ..models import UserBalance, Transaction
from django_cfg.modules.django_logger import get_logger

logger = get_logger("balance_signals")


@receiver(pre_save, sender=UserBalance)
def store_original_balance(sender, instance: UserBalance, **kwargs):
    """Store original balance for change detection."""
    if instance.pk:
        try:
            original = UserBalance.objects.get(pk=instance.pk)
            # Ensure _original_balance is always Decimal
            instance._original_balance = Decimal(str(original.balance_usd)) if original.balance_usd is not None else None
        except UserBalance.DoesNotExist:
            instance._original_balance = None
    else:
        instance._original_balance = None


@receiver(post_save, sender=UserBalance)
def handle_balance_change(sender, instance: UserBalance, created: bool, **kwargs):
    """
    Handle balance changes - only cache clearing and notifications.
    
    Business logic (analytics, calculations) stays in managers.
    """
    if created:
        logger.info(f"New balance created", extra={
            'user_id': instance.user.id,
            'initial_balance': instance.balance_usd
        })
    else:
        # Check if balance changed
        if hasattr(instance, '_original_balance'):
            # Ensure both values are Decimal for consistent arithmetic
            old_balance = Decimal(str(instance._original_balance or 0.0))
            new_balance = Decimal(str(instance.balance_usd))
            
            if old_balance != new_balance:
                balance_change = new_balance - old_balance
                
                logger.info(f"Balance changed", extra={
                    'user_id': instance.user.id,
                    'old_balance': old_balance,
                    'new_balance': new_balance,
                    'change_amount': balance_change
                })
                
                # Check for low balance warning (notification only)
                if new_balance < 10.0 and old_balance >= 10.0:
                    _trigger_low_balance_warning(instance)
                
                # Check for zero balance (notification only)
                if new_balance <= 0.0 and old_balance > 0.0:
                    _handle_zero_balance(instance)
    
    # Clear balance-related caches
    _clear_balance_caches(instance.user.id)


@receiver(post_save, sender=Transaction)
def handle_transaction_creation(sender, instance: Transaction, created: bool, **kwargs):
    """
    Handle transaction creation - only logging and cache clearing.
    
    Business logic (analytics, balance updates) stays in managers.
    """
    if created:
        logger.info(f"New transaction created", extra={
            'transaction_id': str(instance.id),
            'user_id': instance.user.id,
            'transaction_type': instance.transaction_type,
            'amount': instance.amount_usd,
            'payment_id': str(instance.payment_id) if instance.payment_id else None
        })
        
        # Clear related caches
        _clear_balance_caches(instance.user.id)


@receiver(post_delete, sender=Transaction)
def handle_transaction_deletion(sender, instance: Transaction, **kwargs):
    """Handle transaction deletion (should be rare)."""
    logger.warning(f"Transaction deleted", extra={
        'transaction_id': str(instance.id),
        'user_id': instance.user.id,
        'transaction_type': instance.transaction_type,
        'amount': instance.amount,
        'deletion_timestamp': timezone.now().isoformat()
    })
    
    # Clear caches
    _clear_balance_caches(instance.user.id)


# Helper functions (notifications and caching only)

def _trigger_low_balance_warning(balance: UserBalance):
    """Trigger low balance warning for user (notification only)."""
    try:
        logger.warning(f"Low balance warning", extra={
            'user_id': balance.user.id,
            'current_balance': balance.balance_usd,
            'threshold': 10.0
        })
        
        # Set warning flag in cache for frontend
        cache.set(
            f"low_balance_warning:{balance.user.id}",
            {
                'balance': balance.balance_usd,
                'timestamp': timezone.now().isoformat(),
                'threshold': 10.0
            },
            timeout=86400  # 24 hours
        )
        
    except Exception as e:
        logger.error(f"Failed to trigger low balance warning: {e}")


def _handle_zero_balance(balance: UserBalance):
    """Handle zero balance situation (notification only)."""
    try:
        logger.warning(f"Zero balance reached", extra={
            'user_id': balance.user.id,
            'previous_balance': getattr(balance, '_original_balance', 'unknown')
        })
        
        # Set zero balance flag in cache
        cache.set(
            f"zero_balance:{balance.user.id}",
            {
                'timestamp': timezone.now().isoformat(),
                'previous_balance': getattr(balance, '_original_balance', Decimal('0.0'))
            },
            timeout=86400 * 7  # 7 days
        )
        
    except Exception as e:
        logger.error(f"Failed to handle zero balance: {e}")


def _clear_balance_caches(user_id: int):
    """Clear all balance-related cache entries for user."""
    try:
        cache_keys = [
            f"user_balance:{user_id}",
            f"user_transactions:{user_id}",
            f"balance_summary:{user_id}",
            f"balance_history:{user_id}",
            f"transaction_stats:{user_id}",
        ]
        
        cache.delete_many(cache_keys)
        
        logger.debug(f"Cleared balance caches", extra={
            'user_id': user_id,
            'cache_keys_cleared': len(cache_keys)
        })
        
    except Exception as e:
        logger.warning(f"Failed to clear balance caches: {e}")