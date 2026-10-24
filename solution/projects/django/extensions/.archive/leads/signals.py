"""
Lead Signals - Django signals for Lead model.

Uses LeadNotificationService for threaded, non-blocking notifications.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lead


@receiver(post_save, sender=Lead)
def notify_new_lead(sender, instance: Lead, created: bool, **kwargs):
    """Send notifications when a new lead is created."""
    if not created:
        return

    from .services.notification_service import lead_notifications

    lead_notifications.lead_created(instance)
