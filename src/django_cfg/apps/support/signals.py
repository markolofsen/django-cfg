from django.db.models.signals import post_save
from django.dispatch import receiver
import traceback
import logging
import socket
from smtplib import SMTPException

from .models import Message, Ticket
from .utils.support_email_service import SupportEmailService
from django_cfg.modules.django_telegram import DjangoTelegram

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def notify_on_message(sender, instance: Message, created: bool, **kwargs):
    """Send notifications when a new message is created."""
    logger.info(f"🔔 Signal triggered: Message {instance.uuid} created={created}")
    
    if not created:
        logger.info("   ⏭️ Not a new message, skipping")
        return

    ticket = instance.ticket
    user = ticket.user
    
    logger.info(f"   📝 Message from: {instance.sender.username} (is_staff: {instance.sender.is_staff})")
    logger.info(f"   🎫 Ticket author: {user.username}")
    logger.info(f"   📧 Is from author: {instance.is_from_author}")

    # If message is from staff/admin and NOT from the ticket author, send email to user
    if instance.sender.is_staff and not instance.is_from_author:
        logger.info(f"   ✅ Sending email to {user.email}")
        try:
            email_service = SupportEmailService(user)
            email_service.send_support_reply_email(instance)
            logger.info(f"   📬 Email sent successfully!")
        except (socket.timeout, TimeoutError, SMTPException) as e:
            logger.warning(f"   ⚠️ Email service timeout/error: {e}")
            logger.info(f"   📝 Message processed successfully, email notification failed")
            # Do not re-raise to prevent blocking the main process
        except Exception as e:
            logger.error(f"   ❌ Failed to send email notification: {e}")
            logger.debug(f"   🔍 Exception details: {traceback.format_exc()}")
            # Do not re-raise to prevent blocking the main process
    else:
        logger.info(f"   ⏭️ Not sending email (staff: {instance.sender.is_staff}, from_author: {instance.is_from_author})")

    # If message is from user (not staff), send Telegram notification to admins
    if not instance.sender.is_staff:
        try:
            telegram_service = DjangoTelegram()
            telegram_service.send_info(
                "New support message from user",
                {
                    "User": user.username,
                    "Ticket": str(ticket.uuid),
                    "Subject": ticket.subject,
                    "Message": (
                        instance.text[:100] + "..."
                        if len(instance.text) > 100
                        else instance.text
                    ),
                },
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")


@receiver(post_save, sender=Ticket)
def notify_on_ticket_created(sender, instance: Ticket, created: bool, **kwargs):
    """Send notification when a new ticket is created."""
    if not created:
        return

    try:
        email_service = SupportEmailService(instance.user)
        email_service.send_ticket_created_email(instance)
        logger.info(f"   📬 Ticket creation email sent successfully!")
    except (socket.timeout, TimeoutError, SMTPException) as e:
        logger.warning(f"   ⚠️ Email service timeout/error for ticket creation: {e}")
        logger.info(f"   📝 Ticket created successfully, email notification failed")
    except Exception as e:
        logger.error(f"   ❌ Failed to send ticket creation email: {e}")
        logger.debug(f"   🔍 Exception details: {traceback.format_exc()}")
