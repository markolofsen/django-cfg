"""
Auto-configuring Email Service for django_cfg.

This email service automatically configures itself based on the DjangoConfig instance
without requiring manual parameter passing.
"""

from .service import DjangoEmailService
from .utils import (
    get_admin_emails,
    send_admin_email,
    send_admin_notification,
    send_email,
)

__all__ = [
    "DjangoEmailService",
    "send_email",
    "get_admin_emails",
    "send_admin_email",
    "send_admin_notification",
]
