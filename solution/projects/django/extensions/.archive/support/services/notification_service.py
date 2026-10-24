"""
Support Notification Service.

Sends notifications about support events via email and telegram.
All methods are non-blocking (threaded).
"""

import logging
from typing import TYPE_CHECKING

from django_cfg.modules.django_email import send_admin_notification

from ..utils.support_email_service import SupportEmailService

if TYPE_CHECKING:
    from ..models import Message, Ticket

logger = logging.getLogger(__name__)


class SupportNotificationService:
    """
    Notification service for support-related events.

    All methods are non-blocking - emails sent in background threads,
    telegram messages queued with priority.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # Ticket Events
    # ─────────────────────────────────────────────────────────────────────────

    def ticket_created(self, ticket: "Ticket") -> None:
        """
        Notify about new ticket creation.

        - User: confirmation email
        - Admin: email + telegram
        """
        # User email
        try:
            email_service = SupportEmailService(ticket.user)
            email_service.send_ticket_created_email(ticket)
        except Exception as e:
            logger.error("Failed to send ticket created email to user", extra={
                'ticket_id': str(ticket.uuid),
                'error': str(e),
            })

        # Admin notification
        send_admin_notification(
            subject=f"New support ticket: {ticket.subject}",
            message=(
                f"User: {ticket.user.email}\n"
                f"Subject: {ticket.subject}\n"
                f"Ticket ID: {ticket.uuid.hex[:8]}"
            ),
        )

    def ticket_resolved(self, ticket: "Ticket") -> None:
        """Notify user when ticket is resolved (email)."""
        try:
            email_service = SupportEmailService(ticket.user)
            email_service.send_ticket_resolved_email(ticket)
        except Exception as e:
            logger.error("Failed to send ticket resolved email", extra={
                'ticket_id': str(ticket.uuid),
                'error': str(e),
            })

    def ticket_status_changed(self, ticket: "Ticket", old_status: str, new_status: str) -> None:
        """Notify user when ticket status changes (email)."""
        try:
            email_service = SupportEmailService(ticket.user)
            email_service.send_ticket_status_changed_email(ticket, old_status, new_status)
        except Exception as e:
            logger.error("Failed to send ticket status changed email", extra={
                'ticket_id': str(ticket.uuid),
                'old_status': old_status,
                'new_status': new_status,
                'error': str(e),
            })

    # ─────────────────────────────────────────────────────────────────────────
    # Message Events
    # ─────────────────────────────────────────────────────────────────────────

    def message_from_user(self, message: "Message") -> None:
        """
        Notify admin about new message from user (email + telegram).

        Called when ticket author sends a message.
        """
        ticket = message.ticket
        message_preview = message.text[:200] + "..." if len(message.text) > 200 else message.text

        send_admin_notification(
            subject=f"Support message: {ticket.subject}",
            message=(
                f"User: {ticket.user.email}\n"
                f"Ticket: {ticket.subject}\n"
                f"Ticket ID: {ticket.uuid.hex[:8]}\n\n"
                f"Message:\n{message_preview}"
            ),
        )

    def message_from_staff(self, message: "Message") -> None:
        """
        Notify user about staff reply (email).

        Called when staff member replies to a ticket.
        """
        try:
            email_service = SupportEmailService(message.ticket.user)
            email_service.send_support_reply_email(message)
        except Exception as e:
            logger.error("Failed to send staff reply email", extra={
                'message_id': str(message.uuid),
                'ticket_id': str(message.ticket.uuid),
                'error': str(e),
            })


# Singleton instance
support_notifications = SupportNotificationService()
