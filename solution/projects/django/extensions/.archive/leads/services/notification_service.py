"""
Lead Notification Service.

Sends notifications about lead events via email and telegram.
All methods are non-blocking (threaded).
"""

from typing import TYPE_CHECKING

from django_cfg.modules.django_email import send_admin_notification
from django_cfg.modules.django_telegram import DjangoTelegram

if TYPE_CHECKING:
    from ..models import Lead


class LeadNotificationService:
    """
    Notification service for lead-related events.

    All methods are non-blocking - emails sent in background threads,
    telegram messages queued with priority.
    """

    def lead_created(self, lead: "Lead") -> None:
        """Notify admin about new lead (email + telegram)."""
        message_preview = lead.message[:200] + "..." if len(lead.message) > 200 else lead.message

        send_admin_notification(
            subject=f"New lead: {lead.name}",
            message=(
                f"Name: {lead.name}\n"
                f"Email: {lead.email}\n"
                f"Company: {lead.company or 'N/A'}\n"
                f"Site: {lead.site_url}\n"
                f"Subject: {lead.subject or 'N/A'}\n"
                f"Message: {message_preview}"
            ),
        )

    def lead_converted(self, lead: "Lead") -> None:
        """Notify admin about converted lead (telegram)."""
        DjangoTelegram.send_success(
            f"Lead converted: {lead.name}",
            details={
                "email": lead.email,
                "company": lead.company or "N/A",
                "site": lead.site_url,
            },
        )


# Singleton instance
lead_notifications = LeadNotificationService()
