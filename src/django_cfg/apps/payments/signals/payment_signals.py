"""
🔄 Universal Payment Signals

Automatic payment processing and balance management via Django signals.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
from django_cfg.modules.django_logger import get_logger

from ..models import UniversalPayment, UserBalance, Transaction
from ..services.cache import SimpleCache
from django.core.cache import cache

logger = get_logger("payment_signals")


@receiver(pre_save, sender=UniversalPayment)
def store_original_payment_status(sender, instance, **kwargs):
    """Store original payment status for change detection."""
    if instance.pk:
        try:
            old_instance = UniversalPayment.objects.get(pk=instance.pk)
            instance._original_status = old_instance.status
        except UniversalPayment.DoesNotExist:
            instance._original_status = None


@receiver(post_save, sender=UniversalPayment)
def process_payment_status_changes(sender, instance, created, **kwargs):
    """Process payment status changes and update user balance."""
    if created:
        logger.info(f"New payment created: {instance.internal_payment_id} for user {instance.user.email}")
        return
    
    # Check if status changed to completed
    if hasattr(instance, '_original_status'):
        old_status = instance._original_status
        new_status = instance.status
        
        if old_status != new_status:
            logger.info(
                f"Payment status changed: {instance.internal_payment_id} "
                f"for user {instance.user.email} - {old_status} → {new_status}"
            )
            
            # Process completed payment
            if new_status == UniversalPayment.PaymentStatus.COMPLETED and old_status != new_status:
                _process_completed_payment(instance)


def _process_completed_payment(payment: UniversalPayment):
    """Process completed payment and add funds to user balance."""
    try:
        with transaction.atomic():
            # Get or create user balance
            balance, created = UserBalance.objects.get_or_create(
                user=payment.user,
                defaults={
                    'amount_usd': 0,
                    'reserved_usd': 0
                }
            )
            
            # Add funds to balance
            old_balance = balance.amount_usd
            balance.amount_usd += payment.amount_usd
            balance.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=payment.user,
                transaction_type=Transaction.TransactionType.PAYMENT,
                amount_usd=payment.amount_usd,
                balance_before=old_balance,
                balance_after=balance.amount_usd,
                description=f"Payment completed: {payment.internal_payment_id}",
                payment=payment,
                metadata={
                    'provider': payment.provider,
                    'provider_payment_id': payment.provider_payment_id,
                    'amount_usd': str(payment.amount_usd),
                    'currency_code': payment.currency_code
                }
            )
            
            # Mark payment as processed
            payment.processed_at = timezone.now()
            payment.save(update_fields=['processed_at'])
            
            # Clear Redis cache for user
            try:
                # Invalidate user cache using Django cache
                user_cache_pattern = f"payments:user:{payment.user.id}:*"
                # Note: Django cache doesn't support pattern deletion, so we clear specific keys
                cache.delete_many([
                    f"payments:user:{payment.user.id}:balance",
                    f"payments:user:{payment.user.id}:api_keys",
                    f"payments:user:{payment.user.id}:subscriptions"
                ])
            except Exception as e:
                logger.warning(f"Failed to clear Redis cache for user {payment.user.id}: {e}")
            
            logger.info(
                f"Payment {payment.internal_payment_id} processed successfully. "
                f"User {payment.user.email} balance: ${balance.amount_usd}"
            )
            
    except Exception as e:
        logger.error(f"Error processing completed payment {payment.internal_payment_id}: {e}")
        raise


@receiver(post_save, sender=UniversalPayment)
def log_payment_webhook_data(sender, instance, created, **kwargs):
    """Log webhook data for audit purposes."""
    if not created and instance.webhook_data:
        logger.info(
            f"Webhook data received for payment {instance.internal_payment_id}: "
            f"status={instance.status}, provider={instance.provider}"
        )


@receiver(post_save, sender=Transaction)
def log_transaction_creation(sender, instance, created, **kwargs):
    """Log transaction creation for audit trail."""
    if created:
        logger.info(
            f"New transaction: {instance.transaction_type} "
            f"${instance.amount_usd} for user {instance.user.email} "
            f"(balance: ${instance.balance_after})"
        )
