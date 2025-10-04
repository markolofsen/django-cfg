"""
Lead Signals - Django signals for Lead model.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Lead
from django_cfg.modules.django_telegram import DjangoTelegram


@receiver(post_save, sender=Lead)
def notify_new_lead(sender, instance, created, **kwargs):
    """
    Send Telegram notification when a new lead is created.
    
    Args:
        sender: The model class (Lead)
        instance: The Lead instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        try:
            # Prepare notification data
            notification_data = {
                "Name": instance.name,
                "Email": instance.email,
                "Company": instance.company or "Not specified",
                "Contact Type": instance.get_contact_type_display(),
                "Contact Value": instance.contact_value or "Not specified",
                "Subject": instance.subject or "No subject",
                "Site URL": instance.site_url,
                "Status": instance.get_status_display(),
                "Created At": instance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            
            # Add extra data if available
            if instance.extra:
                notification_data["Extra Data"] = instance.extra
            
            # Add company site if available
            if instance.company_site:
                notification_data["Company Site"] = instance.company_site
            
            # Truncate message if too long
            message_preview = instance.message[:200] + "..." if len(instance.message) > 200 else instance.message
            notification_data["Message Preview"] = message_preview
            
            # Send success notification
            DjangoTelegram.send_success(
                f"New lead received from {instance.site_url}",
                notification_data
            )
            
        except Exception as e:
            # Send error notification if something goes wrong
            DjangoTelegram.send_error(
                f"Failed to process new lead notification: {str(e)}",
                {
                    "Lead ID": instance.id,
                    "Lead Name": instance.name,
                    "Lead Email": instance.email,
                    "Error": str(e)
                }
            )
