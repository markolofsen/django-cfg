"""
Django signals for automatic email notifications on user account changes.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone

from .utils.auth_email_service import AuthEmailService
from django_cfg.modules.django_telegram import DjangoTelegram

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_user_registration_email(sender, instance, created, **kwargs):
    """Send welcome email when new user is created - DISABLED for manual control."""
    # Welcome emails should only be sent through views, not automatically via signals
    # This prevents unwanted emails during imports, admin creation, etc.
    pass


@receiver(pre_save, sender=User)
def send_user_status_change_emails(sender, instance, **kwargs):
    """Send emails when user status changes (activation, deactivation)."""
    try:
        # Get the old instance from database
        if instance.pk:
            old_instance = User.objects.get(pk=instance.pk)
            
            # Check if user was activated
            if not old_instance.is_active and instance.is_active:
                email_service = AuthEmailService(instance)
                email_service.send_account_activated_email()
                logger.info(f"Account activation email sent to {instance.email}")
            
            # Check if user was deactivated
            elif old_instance.is_active and not instance.is_active:
                email_service = AuthEmailService(instance)
                email_service.send_account_locked_email("Account deactivated by administrator")
                logger.info(f"Account deactivation email sent to {instance.email}")
                
    except User.DoesNotExist:
        # New user, no old instance to compare
        pass
    except Exception as e:
        logger.error(f"Failed to send status change email to {instance.email}: {e}")


@receiver(pre_save, sender=User)
def send_user_profile_update_email(sender, instance, **kwargs):
    """Send email when user profile is updated (for important changes)."""
    try:
        # Get the old instance from database
        if instance.pk:
            old_instance = User.objects.get(pk=instance.pk)
            
            # Check for important changes
            changes = []
            
            if old_instance.email != instance.email:
                changes.append("email address")
            
            if old_instance.username != instance.username:
                changes.append("username")
            
            if old_instance.first_name != instance.first_name or old_instance.last_name != instance.last_name:
                changes.append("name")
            
            # Send notification if there were important changes
            if changes:
                email_service = AuthEmailService(instance)
                change_text = ", ".join(changes)
                email_service.send_security_alert_email(
                    "Profile Updated",
                    f"Your {change_text} has been updated. If this wasn't you, please contact support immediately."
                )
                logger.info(f"Profile update notification sent to {instance.email}")
                
    except User.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Failed to send profile update email to {instance.email}: {e}")


@receiver(post_save, sender=User)
def send_user_login_notification(sender, instance, created, **kwargs):
    """Send login notification email (triggered by login events)."""
    if not created and hasattr(instance, '_login_time'):
        try:
            email_service = AuthEmailService(instance)
            login_time = instance._login_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            ip_address = getattr(instance, '_login_ip', None)
            
            email_service.send_login_notification_email(login_time, ip_address)
            logger.info(f"Login notification sent to {instance.email}")
            
            # Clean up temporary attributes
            delattr(instance, '_login_time')
            if hasattr(instance, '_login_ip'):
                delattr(instance, '_login_ip')
                
        except Exception as e:
            logger.error(f"Failed to send login notification to {instance.email}: {e}")


# Helper function to trigger login notification
def trigger_login_notification(user, ip_address=None):
    """Helper function to trigger login notification email."""
    user._login_time = timezone.now()
    if ip_address:
        user._login_ip = ip_address
    # Use a field that exists in the model to trigger save
    user.save(update_fields=['email'])  # Trigger save signal without actual changes


# Helper function to send security alerts via Telegram
def send_security_telegram_alert(title: str, user_email: str, details: dict):
    """Send security alert via Telegram."""
    try:
        
        alert_data = {
            "User": user_email,
            "Alert Type": title,
            "Timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            **details
        }
        
        DjangoTelegram.send_warning(f"Security Alert: {title}", alert_data)
        logger.info(f"Security Telegram alert sent: {title} for {user_email}")
        
    except ImportError:
        logger.warning("django_cfg DjangoTelegram not available for security alerts")
    except Exception as e:
        logger.error(f"Failed to send security Telegram alert: {e}")


# Helper function to notify about failed OTP attempts
def notify_failed_otp_attempt(email: str, ip_address: str = None, reason: str = "Invalid OTP"):
    """Send notification about failed OTP attempt."""
    try:
        details = {
            "Reason": reason,
            "IP Address": ip_address or "Unknown",
            "Attempt Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        
        send_security_telegram_alert("Failed OTP Attempt", email, details)
        
    except Exception as e:
        logger.error(f"Failed to send failed OTP notification: {e}") 