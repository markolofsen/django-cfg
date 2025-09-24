"""
Authentication Email Service - Email notifications for authentication operations
"""

import logging
from django.contrib.auth import get_user_model
from django_cfg.modules.django_email import DjangoEmailService
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthEmailService:
    """Service for sending authentication-related email notifications."""

    def __init__(self, user: User):
        self.user = user

    def _send_email(
        self,
        subject: str,
        main_text: str,
        main_html_content: str,
        secondary_text: str,
        button_text: str,
        button_url: str = None,
        template_name: str = "emails/base_email",
    ):
        """Private method for sending templated emails."""
        email_service = DjangoEmailService()
        
        # Prepare context for template
        context = {
            "user": self.user,
            "subject": subject,
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

    def send_otp_email(self, otp_code: str, otp_link: str):
        """Send OTP email notification."""
        self._send_email(
            subject=f"Your OTP code: {otp_code}",
            main_text="Use the code below or click the button to authenticate:",
            main_html_content=f'<p style="font-size: 2em; font-weight: bold; color: #007bff;">{otp_code}</p>',
            secondary_text="This code expires in 10 minutes.",
            button_text="Login with OTP",
            button_url=otp_link,
        )

    def send_welcome_email(self, username: str):
        """Send welcome email for new user registration."""
        app_name = getattr(settings, 'PROJECT_NAME', 'Our App')
        dashboard_url = getattr(settings, 'DASHBOARD_URL', '/')
        
        self._send_email(
            subject=f"Welcome to {app_name}",
            main_text=f"Welcome {username}! Your account has been successfully created.",
            main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Welcome {username}!</p>',
            secondary_text="You can now access all our services and start exploring our API.",
            button_text="Go to Dashboard",
            button_url=dashboard_url,
        )

    def send_security_alert_email(self, alert_type: str, details: str):
        """Send security alert email."""
        self._send_email(
            subject=f"Security Alert: {alert_type} ⚠️",
            main_text=f"A security alert has been triggered for your account.",
            main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">{alert_type}</p>',
            secondary_text=f"Details: {details}\nIf this wasn't you, please contact support immediately.",
            button_text="Review Account",
        )
