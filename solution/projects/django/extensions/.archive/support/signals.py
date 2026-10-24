"""
Support Signals - Django signals for Support models.

Uses SupportNotificationService for threaded, non-blocking notifications.
"""

import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Message, Ticket

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Ticket)
def handle_ticket_created(sender, instance: Ticket, created: bool, **kwargs):
    """Send notifications when a new ticket is created."""
    if not created:
        return

    from .services.notification_service import support_notifications

    support_notifications.ticket_created(instance)


@receiver(pre_save, sender=Ticket)
def handle_ticket_status_change(sender, instance: Ticket, **kwargs):
    """
    Handle ticket status changes.

    - resolved: send resolved notification
    - other changes: send status changed notification
    """
    if not instance.pk:
        return

    try:
        old_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        return

    old_status = old_instance.status
    new_status = instance.status

    if old_status == new_status:
        return

    from .services.notification_service import support_notifications

    if new_status == Ticket.TicketStatus.RESOLVED:
        support_notifications.ticket_resolved(instance)
    else:
        support_notifications.ticket_status_changed(instance, old_status, new_status)


@receiver(post_save, sender=Message)
def handle_message_created(sender, instance: Message, created: bool, **kwargs):
    """
    Send notifications when a new message is created.

    - From user (ticket author): notify admin (telegram)
    - From staff: notify user (email)
    """
    if not created:
        return

    from .services.notification_service import support_notifications

    if instance.is_from_author:
        # User sent a message -> notify admin
        support_notifications.message_from_user(instance)
    elif instance.sender.is_staff:
        # Staff replied -> notify user
        support_notifications.message_from_staff(instance)
