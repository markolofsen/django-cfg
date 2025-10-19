"""
Email OTP service using SendGrid.

Provides OTP delivery via email with template support and
comprehensive deliverability optimization.
"""

import logging
from typing import Any, Dict, Optional, Tuple

from django_cfg.modules.django_twilio._imports import SendGridAPIClient

# Import Mail helper conditionally
try:
    from sendgrid.helpers.mail import Mail
except ImportError:
    Mail = None  # type: ignore

from asgiref.sync import sync_to_async

from .base import BaseTwilioService
from .exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
)
from .models import SendGridConfig

logger = logging.getLogger(__name__)


class EmailOTPService(BaseTwilioService):
    """
    Email OTP service using SendGrid.

    Provides OTP delivery via email with template support and
    comprehensive deliverability optimization.
    """

    def send_otp(
        self,
        email: str,
        subject: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, str]:
        """
        Send OTP via email.

        Args:
            email: Recipient email address
            subject: Custom email subject (uses default if not provided)
            template_data: Additional data for email template

        Returns:
            Tuple[bool, str, str]: (success, message, otp_code)

        Raises:
            TwilioConfigurationError: If SendGrid is not configured
            TwilioSendError: If email sending fails
        """
        config = self.get_twilio_config()

        if not config.sendgrid:
            raise TwilioConfigurationError(
                "SendGrid configuration not found",
                missing_fields=["sendgrid"],
                suggestions=["Configure SendGridConfig in your Twilio settings"]
            )

        sendgrid_client = self.get_sendgrid_client()
        if not sendgrid_client:
            raise TwilioConfigurationError("SendGrid client not initialized")

        try:
            # Generate OTP code
            otp_code = self._generate_otp(6)

            # Store OTP for verification
            self._store_otp(email, otp_code, config.verify.ttl_seconds if config.verify else 600)

            # Prepare email content
            if config.sendgrid.otp_template_id:
                # Use dynamic template
                success, message = self._send_template_email(
                    sendgrid_client, config.sendgrid, email, otp_code, template_data
                )
            else:
                # Use simple HTML email
                success, message = self._send_simple_email(
                    sendgrid_client, config.sendgrid, email, otp_code, subject
                )

            if success:
                logger.info(f"Email OTP sent successfully to {self._mask_identifier(email)}")
                return True, message, otp_code
            else:
                raise TwilioSendError(message, channel="email", recipient=email)

        except Exception as e:
            if isinstance(e, TwilioSendError):
                raise
            raise TwilioSendError(
                f"Failed to send email OTP: {e}",
                channel="email",
                recipient=email
            ) from e

    async def asend_otp(
        self,
        email: str,
        subject: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, str]:
        """Async version of send_otp."""
        return await sync_to_async(self.send_otp)(email, subject, template_data)

    def _send_template_email(
        self,
        client: SendGridAPIClient,
        config: SendGridConfig,
        email: str,
        otp_code: str,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Send email using SendGrid dynamic template."""
        try:
            # Prepare template data
            dynamic_data = {
                'verification_code': otp_code,
                'user_email': email,
                'expiry_minutes': 10,
                'company_name': config.from_name,
                **config.custom_template_data,
                **(template_data or {})
            }

            message = Mail(
                from_email=(config.from_email, config.from_name),
                to_emails=email
            )

            message.template_id = config.otp_template_id
            message.dynamic_template_data = dynamic_data

            if config.reply_to_email:
                message.reply_to = config.reply_to_email

            response = client.send(message)

            if response.status_code in [200, 201, 202]:
                return True, f"OTP sent via email template to {self._mask_identifier(email)}"
            else:
                return False, f"SendGrid API error: {response.status_code}"

        except Exception as e:
            return False, f"Template email error: {e}"

    def _send_simple_email(
        self,
        client: SendGridAPIClient,
        config: SendGridConfig,
        email: str,
        otp_code: str,
        subject: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Send simple HTML email without template."""
        try:
            html_content = self._generate_html_content(otp_code, config.from_name)
            plain_content = self._generate_plain_content(otp_code)

            message = Mail(
                from_email=(config.from_email, config.from_name),
                to_emails=email,
                subject=subject or config.default_subject,
                html_content=html_content,
                plain_text_content=plain_content
            )

            if config.reply_to_email:
                message.reply_to = config.reply_to_email

            response = client.send(message)

            if response.status_code in [200, 201, 202]:
                return True, f"OTP sent via email to {self._mask_identifier(email)}"
            else:
                return False, f"SendGrid API error: {response.status_code}"

        except Exception as e:
            return False, f"Simple email error: {e}"

    def _generate_html_content(self, otp_code: str, company_name: str) -> str:
        """Generate HTML email content."""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h1 style="color: #333; margin-bottom: 20px;">Verification Code</h1>
                <p style="color: #666; font-size: 16px; margin-bottom: 30px;">
                    Your verification code is:
                </p>
                <div style="background-color: #007bff; color: white; font-size: 32px; font-weight: bold;
                     padding: 20px; border-radius: 8px; letter-spacing: 5px; margin: 30px 0;">
                    {otp_code}
                </div>
                <p style="color: #999; font-size: 14px;">
                    This code expires in 10 minutes<br>
                    If you didn't request this code, please ignore this email
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Sent by {company_name}
                </p>
            </div>
        </div>
        """

    def _generate_plain_content(self, otp_code: str) -> str:
        """Generate plain text email content."""
        return f"""
Your verification code: {otp_code}

This code expires in 10 minutes.
If you didn't request this code, please ignore this email.
        """.strip()


__all__ = [
    "EmailOTPService",
]
