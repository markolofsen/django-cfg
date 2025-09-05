"""
Support Email Service - Email notifications for support operations
"""

import logging
from django.contrib.auth import get_user_model
from django_cfg.modules.django_email import DjangoEmailService

User = get_user_model()
logger = logging.getLogger(__name__)


class SupportEmailService:
    """Service for sending support-related email notifications."""

    def __init__(self, user: User):
        self.user = user
    
    def _get_ticket_url(self, ticket_uuid: str) -> str:
        """Get ticket URL from configuration."""
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'get_ticket_url'):
                return config.get_ticket_url(str(ticket_uuid))
            else:
                # Fallback URL if config is not available
                return f"#ticket-{ticket_uuid}"
        except Exception as e:
            logger.warning(f"Could not generate ticket URL: {e}")
            return f"#ticket-{ticket_uuid}"

    def _send_email(
        self,
        subject: str,
        main_text: str,
        main_html_content: str = None,
        secondary_text: str = None,
        button_text: str = None,
        button_url: str = None,
        template_name: str = "emails/base_email",
    ):
        """Private method for sending templated emails."""
        email_service = DjangoEmailService()
        
        # Prepare context for template
        context = {
            "user": self.user,
            "email_title": subject,
            "greeting": f"Hello {self.user.get_full_name() or self.user.username or 'there'}",
            "main_text": main_text,
            "main_html_content": main_html_content,
            "secondary_text": secondary_text,
            "button_text": button_text,
            "button_url": button_url,
        }
        
        email_service.send_template(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[self.user.email],
        )

    def send_ticket_created_email(self, ticket):
        """Send email notification when a new ticket is created."""
        self._send_email(
            subject=f"Ticket Created: {ticket.subject}",
            main_text="Your support ticket has been successfully created. Our team will review it and respond soon.",
            main_html_content=f'<div style="background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0;"><strong>Ticket #{ticket.uuid.hex[:8]}</strong><br><strong>Subject:</strong> {ticket.subject}</div>',
            secondary_text="You will receive email notifications when our support team replies to your ticket.",
            button_text="View Ticket",
            button_url=self._get_ticket_url(ticket.uuid),
        )

    def send_support_reply_email(self, message):
        """Send email notification when support replies to a ticket."""
        ticket = message.ticket
        
        # Don't send email to yourself
        if message.sender == ticket.user:
            return
            
        self._send_email(
            subject=f"Support Reply: {ticket.subject}",
            main_text="You have received a reply from our support team.",
            main_html_content=f'<div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0;"><strong>Support Reply:</strong><br>{message.text}</div>',
            secondary_text="Please reply to continue the conversation. We're here to help!",
            button_text="View & Reply",
            button_url=self._get_ticket_url(ticket.uuid),
        )

    def send_ticket_status_changed_email(self, ticket, old_status, new_status):
        """Send email notification when ticket status changes."""
        status_colors = {
            'open': '#28a745',
            'in_progress': '#ffc107', 
            'resolved': '#17a2b8',
            'closed': '#6c757d',
        }
        
        color = status_colors.get(new_status, '#6c757d')
        
        self._send_email(
            subject=f"Ticket Status Updated: {ticket.subject}",
            main_text=f"Your ticket status has been updated from '{old_status}' to '{new_status}'.",
            main_html_content=f'<div style="background: #f8f9fa; padding: 15px; border-left: 4px solid {color}; margin: 15px 0;"><strong>Status Update:</strong><br>From: <span style="color: #6c757d;">{old_status}</span><br>To: <span style="color: {color}; font-weight: bold;">{new_status}</span></div>',
            secondary_text="If you have any questions about this status change, please reply to your ticket.",
            button_text="View Ticket",
            button_url=self._get_ticket_url(ticket.uuid),
        )

    def send_ticket_resolved_email(self, ticket):
        """Send email notification when ticket is resolved."""
        self._send_email(
            subject=f"Ticket Resolved: {ticket.subject}",
            main_text="Great news! Your support ticket has been resolved.",
            main_html_content=f'<div style="background: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0;"><strong>✅ Ticket Resolved</strong><br>Your issue has been successfully resolved by our support team.</div>',
            secondary_text="If you're satisfied with the resolution, no further action is needed. If you need additional help, feel free to reply to reopen the ticket.",
            button_text="View Resolution",
            button_url=self._get_ticket_url(ticket.uuid),
        )
