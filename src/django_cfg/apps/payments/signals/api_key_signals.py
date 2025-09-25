"""
🔄 Universal API Keys Auto-Creation Signals

Automatic API key creation and management via Django signals.
Enhanced version of CarAPI signals with universal support.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django_cfg.modules.django_logger import get_logger

from ..models import APIKey

User = get_user_model()
logger = get_logger("api_key_signals")


@receiver(post_save, sender=User)
def create_default_api_key(sender, instance, created, **kwargs):
    """
    Automatically create default API key for new users.
    This ensures every user can immediately start using the API.
    """
    if created:
        try:
            with transaction.atomic():
                import secrets
                key_value = f"ak_{secrets.token_urlsafe(32)}"
                
                api_key = APIKey.objects.create(
                    user=instance,
                    name="Default API Key",
                    key_value=key_value,
                    key_prefix=key_value[:8],
                    is_active=True
                )
                
                logger.info(
                    f"Created default API key for user {instance.email}: {api_key.key_prefix}***"
                )
                
                # Optional: Send welcome email with API key info
                # This would be handled in custom project implementations
                # from .tasks import send_api_key_welcome_email
                # send_api_key_welcome_email.delay(instance.id, api_key.id)
                
        except Exception as e:
            logger.error(f"Failed to create default API key for user {instance.email}: {e}")


@receiver(post_save, sender=User)
def ensure_user_has_api_key(sender, instance, **kwargs):
    """
    Ensure user always has at least one API key.
    Creates one if user has no active keys.
    """
    # Skip if this is a new user (handled by create_default_api_key)
    if kwargs.get('created', False):
        return
    
    # Check if user has any active keys
    if not APIKey.objects.filter(user=instance, is_active=True).exists():
        try:
            with transaction.atomic():
                import secrets
                key_value = f"ak_{secrets.token_urlsafe(32)}"
                
                api_key = APIKey.objects.create(
                    user=instance,
                    name="Recovery API Key",
                    key_value=key_value,
                    key_prefix=key_value[:8],
                    is_active=True
                )
                logger.info(
                    f"Created recovery API key for user {instance.email}: {api_key.key_prefix}***"
                )
        except Exception as e:
            logger.error(f"Failed to create recovery API key for user {instance.email}: {e}")


@receiver(pre_save, sender=APIKey)
def store_original_status(sender, instance, **kwargs):
    """Store original status for change detection."""
    if instance.pk:
        try:
            old_instance = APIKey.objects.get(pk=instance.pk)
            instance._original_is_active = old_instance.is_active
        except APIKey.DoesNotExist:
            instance._original_is_active = None


@receiver(post_save, sender=APIKey)
def log_api_key_changes(sender, instance, created, **kwargs):
    """Log API key creation and status changes for security monitoring."""
    if created:
        logger.info(
            f"New API key created: {instance.name} ({instance.key_prefix}***) "
            f"for user {instance.user.email}"
        )
    else:
        # Check if status changed
        if hasattr(instance, '_original_is_active'):
            old_status = instance._original_is_active
            new_status = instance.is_active
            
            if old_status is not None and old_status != new_status:
                status_text = "activated" if new_status else "deactivated"
                logger.warning(
                    f"API key {status_text}: {instance.name} ({instance.key_prefix}***) "
                    f"for user {instance.user.email}"
                )


@receiver(post_save, sender=APIKey)
def update_last_used_on_activation(sender, instance, created, **kwargs):
    """Update last_used when API key is activated."""
    if not created and instance.is_active and hasattr(instance, '_original_is_active'):
        if instance._original_is_active is False and instance.is_active is True:
            # Key was just activated
            APIKey.objects.filter(pk=instance.pk).update(
                last_used=timezone.now()
            )


@receiver(post_delete, sender=APIKey)
def log_api_key_deletion(sender, instance, **kwargs):
    """Log API key deletions for security audit."""
    logger.warning(
        f"API key deleted: {instance.name} ({instance.key_prefix}***) "
        f"for user {instance.user.email} - Status was: {'active' if instance.is_active else 'inactive'}"
    )


@receiver(post_delete, sender=APIKey)
def ensure_user_has_remaining_key(sender, instance, **kwargs):
    """
    Ensure user still has at least one API key after deletion.
    Creates a new one if this was the last active key.
    """
    user = instance.user
    
    # Check if user has any remaining active keys
    if not APIKey.objects.filter(user=user, is_active=True).exists():
        try:
            with transaction.atomic():
                api_key = APIKey.objects.create(
                    user=user,
                    name="Auto Recovery API Key",
                    is_active=True
                )
                logger.info(
                    f"Created auto-recovery API key for user {user.email}: {api_key.key_prefix}*** "
                    f"(previous key was deleted)"
                )
        except Exception as e:
            logger.error(f"Failed to create auto-recovery API key for user {user.email}: {e}")
