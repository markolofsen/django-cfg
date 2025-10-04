"""
Django signals for newsletter application.

Handles automatic email notifications and newsletter management.
"""

import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Newsletter, NewsletterSubscription

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Newsletter)
def newsletter_created(sender, instance, created, **kwargs):
    """Handle newsletter creation."""
    if created:
        logger.info(f"New newsletter created: {instance.title}")
        # Add any additional logic for newsletter creation
        # e.g., notify admins, setup initial subscribers, etc.


@receiver(post_save, sender=NewsletterSubscription)
def subscription_created(sender, instance, created, **kwargs):
    """Handle newsletter subscription creation."""
    if created:
        pass
        # logger.info(f"New subscription: {instance.email} to newsletter {instance.newsletter.title}")
        # # Add logic for welcome email to new subscribers
        # try:
        #     from .services.email_service import NewsletterEmailService
        #     email_service = NewsletterEmailService()
        #     email_service.send_subscription_welcome_email(instance)
        # except Exception as e:
        #     logger.error(f"Failed to send welcome email to {instance.email}: {e}")


@receiver(pre_delete, sender=NewsletterSubscription)
def subscription_deleted(sender, instance, **kwargs):
    """Handle newsletter subscription deletion."""
    logger.info(f"Subscription deleted: {instance.email} from newsletter {instance.newsletter.title}")
    # Add logic for unsubscribe confirmation email
    try:
        from .services.email_service import NewsletterEmailService
        email_service = NewsletterEmailService()
        email_service.send_unsubscribe_confirmation_email(instance)
    except Exception as e:
        logger.error(f"Failed to send unsubscribe confirmation to {instance.email}: {e}")


@receiver(post_save, sender=User)
def auto_subscribe_new_users(sender, instance, created, **kwargs):
    """Automatically subscribe new users to default newsletters."""
    if created and instance.email:
        try:
            # Find newsletters with auto_subscribe enabled
            auto_newsletters = Newsletter.objects.filter(auto_subscribe=True, is_active=True)
            
            for newsletter in auto_newsletters:
                NewsletterSubscription.objects.get_or_create(
                    newsletter=newsletter,
                    email=instance.email,
                    defaults={
                        'user': instance,
                        'is_active': True
                    }
                )
                logger.info(f"Auto-subscribed {instance.email} to {newsletter.title}")
                
        except Exception as e:
            logger.error(f"Failed to auto-subscribe user {instance.email}: {e}")
