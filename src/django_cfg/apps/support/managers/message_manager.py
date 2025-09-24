from django.db import models
import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type checking
    from django_cfg.apps.support.models import Message


class MessageManager(models.Manager):
    def send_support_reply_email(self, message: "Message"):
        """Send email notification when support replies to a ticket."""
        from ..utils.support_email_service import SupportEmailService
        
        ticket = message.ticket
        user = ticket.user
        
        # Don't send email to yourself
        if message.sender == ticket.user:
            return

        # Send email in background thread
        def send_email_async():
            try:
                email_service = SupportEmailService(user)
                email_service.send_support_reply_email(message)
            except Exception as e:
                # Log error but don't raise to avoid blocking the main thread
                print(f"Failed to send support reply email: {e}")

        thread = threading.Thread(target=send_email_async)
        thread.daemon = True  # Thread will be terminated when main process ends
        thread.start()
