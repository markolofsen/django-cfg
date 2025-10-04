"""
Email utilities and convenience functions.
"""

from typing import List, Optional

from .service import DjangoEmailService


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


__all__ = ["send_email"]
