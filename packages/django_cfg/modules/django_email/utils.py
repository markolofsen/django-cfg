"""
Email utilities and convenience functions.
"""

import logging
from typing import List, Optional

from .service import DjangoEmailService

logger = logging.getLogger("django_cfg.email")


def send_email(
    subject: str,
    message: str,
    recipient_list: List[str],
    from_email: Optional[str] = None,
    fail_silently: bool = False,
) -> int:
    """
    Send a simple email using auto-configured service.

    Args:
        subject: Email subject
        message: Email message
        recipient_list: List of recipient email addresses
        from_email: Sender email (auto-detected if not provided)
        fail_silently: Whether to fail silently on errors

    Returns:
        Number of emails sent successfully
    """
    email_service = DjangoEmailService()
    return email_service.send_simple(
        subject=subject,
        message=message,
        recipient_list=recipient_list,
        from_email=from_email,
        fail_silently=fail_silently,
    )


def get_admin_emails() -> List[str]:
    """
    Get admin email addresses from config or Django settings.

    Priority:
    1. config.admin_emails (if defined)
    2. Django ADMINS setting
    3. Empty list

    Returns:
        List of admin email addresses
    """
    try:
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        if config:
            # Check for admin_emails attribute
            admin_emails = getattr(config, "admin_emails", None)
            if admin_emails:
                return list(admin_emails)
    except Exception:
        pass

    # Fallback to Django ADMINS setting
    try:
        from django.conf import settings

        admins = getattr(settings, "ADMINS", [])
        if admins:
            # ADMINS is a list of (name, email) tuples
            return [email for name, email in admins]
    except Exception:
        pass

    return []


def send_admin_email(
    subject: str,
    message: str,
    html_message: Optional[str] = None,
    from_email: Optional[str] = None,
    fail_silently: bool = True,
) -> bool:
    """
    Send email to all admin addresses.

    Gets admin emails from config.admin_emails or Django ADMINS setting.

    Args:
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message
        from_email: Sender email (auto-detected if not provided)
        fail_silently: Whether to fail silently (default True for notifications)

    Returns:
        True if email was queued, False if no admins configured

    Example:
        >>> from django_cfg import send_admin_email
        >>> send_admin_email(
        ...     subject="[Alert] Database Backup Failed",
        ...     message="Backup for 'default' database failed at 2025-01-15 02:00",
        ... )
    """
    admin_emails = get_admin_emails()

    if not admin_emails:
        logger.warning("No admin emails configured - skipping notification")
        return False

    email_service = DjangoEmailService()

    if html_message:
        return email_service.send_html(
            subject=subject,
            html_message=html_message,
            recipient_list=admin_emails,
            text_message=message,
            from_email=from_email,
            fail_silently=fail_silently,
        )
    else:
        return email_service.send_simple(
            subject=subject,
            message=message,
            recipient_list=admin_emails,
            from_email=from_email,
            fail_silently=fail_silently,
        )


def send_admin_notification(
    subject: str,
    message: str,
    html_message: Optional[str] = None,
    send_telegram: bool = True,
    send_email: bool = True,
    fail_silently: bool = True,
) -> dict:
    """
    Send notification to admins via email and/or Telegram.

    This is a convenience function for sending critical notifications
    through multiple channels.

    Args:
        subject: Notification subject (used for email subject and Telegram title)
        message: Plain text message
        html_message: Optional HTML message (email only)
        send_telegram: Whether to send Telegram notification
        send_email: Whether to send email notification
        fail_silently: Whether to fail silently

    Returns:
        Dict with results: {"telegram": bool, "email": bool}

    Example:
        >>> from django_cfg import send_admin_notification
        >>> send_admin_notification(
        ...     subject="Database Backup Completed",
        ...     message="Backup 'default_20250115_020000.sql.gz' created successfully",
        ... )
    """
    results = {"telegram": False, "email": False}

    # Send Telegram notification
    if send_telegram:
        try:
            from ..django_telegram import send_telegram_message

            telegram_text = f"*{subject}*\n\n{message}"
            send_telegram_message(telegram_text, parse_mode="Markdown")
            results["telegram"] = True
        except Exception as e:
            if not fail_silently:
                raise
            logger.debug(f"Telegram notification failed: {e}")

    # Send email notification
    if send_email:
        try:
            results["email"] = send_admin_email(
                subject=subject,
                message=message,
                html_message=html_message,
                fail_silently=fail_silently,
            )
        except Exception as e:
            if not fail_silently:
                raise
            logger.debug(f"Email notification failed: {e}")

    return results


__all__ = [
    "send_email",
    "get_admin_emails",
    "send_admin_email",
    "send_admin_notification",
]
