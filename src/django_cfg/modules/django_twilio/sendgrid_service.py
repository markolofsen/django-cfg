"""
SendGrid service for email delivery.

Handles all SendGrid-specific functionality including:
- Email messaging
- OTP email delivery
- Template support
"""

import logging
import random
import string
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From
from asgiref.sync import sync_to_async
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_twilio.models import TwilioConfig, SendGridConfig
from django_cfg.modules.django_twilio.exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
)

try:
    from django_cfg.apps.accounts.models import CustomUser
except ImportError:
    CustomUser = None

logger = logging.getLogger(__name__)


class SendGridService(BaseCfgModule):
    """
    SendGrid service for email delivery.
    
    Handles email operations with auto-configuration from DjangoConfig.
    """
    
    def __init__(self):
        """Initialize with auto-discovered configuration."""
        super().__init__()
        self._twilio_config: Optional[TwilioConfig] = None
        self._client: Optional[SendGridAPIClient] = None
        self._otp_storage: Dict[str, Dict[str, Any]] = {}  # In-memory storage for OTP codes
    
    def get_twilio_config(self) -> TwilioConfig:
        """Get Twilio configuration (which includes SendGrid config)."""
        if self._twilio_config is None:
            django_config = super().get_config()
            if not django_config:
                raise TwilioConfigurationError(
                    "DjangoConfig instance not found",
                    suggestions=["Ensure DjangoConfig is properly initialized"]
                )
            
            twilio_config = getattr(django_config, 'twilio', None)
            if not twilio_config:
                raise TwilioConfigurationError(
                    "Twilio configuration not found in DjangoConfig",
                    missing_fields=["twilio"],
                    suggestions=["Add TwilioConfig to your DjangoConfig class"]
                )
            
            self._twilio_config = twilio_config
        
        return self._twilio_config
    
    def get_sendgrid_config(self) -> SendGridConfig:
        """Get SendGrid configuration."""
        config = self.get_twilio_config()
        
        if not config.sendgrid:
            raise TwilioConfigurationError(
                "SendGrid configuration not found",
                missing_fields=["sendgrid"],
                suggestions=["Configure SendGridConfig in your Twilio settings"]
            )
        
        return config.sendgrid
    
    def get_client(self) -> SendGridAPIClient:
        """Get or create SendGrid client."""
        if self._client is None:
            config = self.get_sendgrid_config()
            
            try:
                self._client = SendGridAPIClient(
                    api_key=config.api_key.get_secret_value()
                )
                
                logger.info("SendGrid client initialized")
                    
            except Exception as e:
                raise TwilioConfigurationError(
                    f"Failed to initialize SendGrid client: {str(e)}",
                    suggestions=["Check SendGrid API key configuration"]
                )
        
        return self._client
    
    # === Email Methods ===
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a simple email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            plain_content: Plain text content (optional)
            from_email: Sender email (uses config default if not provided)
            from_name: Sender name (uses config default if not provided)
            
        Returns:
            Dictionary with send results
        """
        try:
            client = self.get_client()
            config = self.get_sendgrid_config()
            
            # Use config defaults if not provided
            sender_email = from_email or config.from_email
            sender_name = from_name or config.from_name
            
            message = Mail(
                from_email=(sender_email, sender_name),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            if config.reply_to_email:
                message.reply_to = config.reply_to_email
            
            response = client.send(message)
            
            result = {
                'status_code': response.status_code,
                'success': response.status_code in [200, 201, 202],
                'to_email': to_email,
                'subject': subject,
            }
            
            if result['success']:
                logger.info(f"Email sent successfully to {self._mask_email(to_email)}")
            else:
                logger.error(f"SendGrid API error: {response.status_code}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise TwilioSendError(
                f"Failed to send email: {str(e)}",
                context={'to_email': to_email, 'subject': subject}
            )
    
    # === OTP Methods ===
    
    def send_otp_email(
        self,
        email: str,
        subject: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        otp_code: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Send OTP via email.
        
        Args:
            email: Recipient email address
            subject: Custom email subject (uses default if not provided)
            template_data: Additional data for email template
            otp_code: Use existing OTP code instead of generating new one
            
        Returns:
            Tuple[bool, str, str]: (success, message, otp_code)
        """
        try:
            client = self.get_client()
            config = self.get_sendgrid_config()
            
            # Use provided OTP code or generate new one
            if not otp_code:
                otp_code = self._generate_otp(6)
                # Store OTP for verification (10 minutes TTL)
                self._store_otp(email, otp_code, 600)
            # If OTP code is provided, don't store it (it's already in database)
            
            # Prepare email content
            if config.otp_template_id:
                # Use dynamic template
                success, message = self._send_template_email(
                    client, config, email, otp_code, template_data
                )
            else:
                # Use simple HTML email
                success, message = self._send_simple_otp_email(
                    client, config, email, otp_code, subject
                )
            
            if success:
                logger.info(f"Email OTP sent successfully to {self._mask_email(email)}")
                return True, message, otp_code
            else:
                raise TwilioSendError(message)
                
        except Exception as e:
            if isinstance(e, TwilioSendError):
                raise
            raise TwilioSendError(
                f"Failed to send email OTP: {e}",
                context={'email': email}
            ) from e
    
    def verify_otp(self, email: str, code: str) -> Tuple[bool, str]:
        """
        Verify OTP code.
        
        Args:
            email: Email address used for OTP
            code: OTP code to verify
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        stored_data = self._get_stored_otp(email)
        
        if not stored_data:
            return False, "OTP not found. Please request a new code."
        
        if datetime.now() > stored_data['expires_at']:
            self._remove_otp(email)
            return False, "OTP expired. Please request a new code."
        
        # Increment attempt counter
        stored_data['attempts'] += 1
        
        if stored_data['attempts'] > 5:  # Max attempts
            self._remove_otp(email)
            return False, "Too many attempts. Please request a new code."
        
        if stored_data['code'] == code:
            self._remove_otp(email)
            logger.info(f"Email OTP verified successfully for {self._mask_email(email)}")
            return True, "OTP verified successfully"
        else:
            return False, f"Invalid OTP code. {5 - stored_data['attempts']} attempts remaining."
    
    # === Helper Methods ===
    
    def _get_user_data(self, email: str) -> Tuple[str, str]:
        """
        Retrieves user's full name and username from the database.
        Provides fallback to email prefix if user is not found or an error occurs.
        """
        if CustomUser:
            try:
                user = CustomUser.objects.get(email=email)
                user_full_name = user.get_full_name() or user.display_username or user.username
                user_username = user.username
                return user_full_name, user_username
            except CustomUser.DoesNotExist:
                logger.warning(f"User with email {email} not found for SendGrid template. Using email prefix as fallback.")
            except Exception as e:
                logger.error(f"Error retrieving user data for email {email}: {e}. Using email prefix as fallback.")
        else:
            logger.warning("CustomUser model not available. Using email prefix as fallback for SendGrid template.")

        # Fallback to email prefix
        email_prefix = email.split('@')[0]
        return email_prefix, email_prefix
    
    # === Template Methods ===
    
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
            # Get config for dynamic data
            cfg = self.get_config()
            
            # Get user data for template
            user_full_name, user_username = self._get_user_data(email)
            
            # Prepare subject
            subject = f"Your {cfg.project_name if cfg else 'Django CFG'} verification code"
            
            # Prepare template data matching sendgrid_otp_email.html template
            dynamic_data = {
                'site_name': cfg.project_name if cfg else 'Django CFG',
                'project_name': cfg.project_name if cfg else 'Django CFG', 
                'user_name': user_full_name,  # Real user name
                'user_email': email,
                'user': {
                    'get_full_name': user_full_name,  # Real user name
                    'username': user_username,        # Real username
                    'email': email
                },
                'otp_code': otp_code,  # This is what the template expects!
                'otp_link': cfg.get_otp_url(otp_code) if cfg else None,  # Add OTP verification link
                'expires_minutes': 10,
                'subject': subject,  # Add subject to template data
                **config.custom_template_data,
                **(template_data or {})
            }
            
            message = Mail(
                from_email=(config.from_email, config.from_name),
                to_emails=email
                # subject is handled by dynamic template with {{{subject}}} in SendGrid Console
            )
            
            message.template_id = config.otp_template_id
            message.dynamic_template_data = dynamic_data
            
            if config.reply_to_email:
                message.reply_to = config.reply_to_email
            
            response = client.send(message)
            
            if response.status_code in [200, 201, 202]:
                return True, f"OTP sent via email template to {self._mask_email(email)}"
            else:
                return False, f"SendGrid API error: {response.status_code}"
                
        except Exception as e:
            return False, f"Template email error: {e}"
    
    def _send_simple_otp_email(
        self,
        client: SendGridAPIClient,
        config: SendGridConfig,
        email: str,
        otp_code: str,
        subject: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Send simple HTML email using Django templates."""
        try:
            # Get current config for template context
            from django_cfg.core.config import get_current_config
            current_config = get_current_config()
            
            # Prepare context for unified template
            cfg = self.get_config()
            context = {
                "otp_code": otp_code,
                "expires_minutes": 10,
                "site_name": cfg.project_name if cfg else 'Django CFG',
                "project_name": cfg.project_name if cfg else 'Django CFG',
                "user": {"username": email.split("@")[0]},  # Fallback user object
            }
            
            # Add OTP link if config is available
            if current_config:
                context["otp_link"] = current_config.get_otp_url(otp_code)
            
            # Render Django templates
            try:
                html_content = render_to_string("emails/otp_email.html", context)
                plain_content = render_to_string("emails/otp_email.txt", context)
            except Exception as template_error:
                # Fallback to built-in HTML if template fails
                logger.warning(f"Django template render failed: {template_error}, using fallback HTML")
                html_content = self._generate_html_content(otp_code, config.from_name)
                plain_content = self._generate_plain_content(otp_code)
            
            message = Mail(
                from_email=(config.from_email, config.from_name),
                to_emails=email,
                subject=subject or f"Your {config.from_name} Login Code",
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            if config.reply_to_email:
                message.reply_to = config.reply_to_email
            
            response = client.send(message)
            
            if response.status_code in [200, 201, 202]:
                return True, f"OTP sent via email to {self._mask_email(email)}"
            else:
                return False, f"SendGrid API error: {response.status_code}"
                
        except Exception as e:
            return False, f"Simple email error: {e}"
    
    # === Utility Methods ===
    
    def _generate_otp(self, length: int = 6) -> str:
        """Generate numeric OTP code."""
        return ''.join(random.choices(string.digits, k=length))
    
    def _store_otp(self, email: str, code: str, ttl_seconds: int = 600) -> None:
        """Store OTP code with expiration."""
        self._otp_storage[email] = {
            'code': code,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
            'attempts': 0,
        }
    
    def _get_stored_otp(self, email: str) -> Optional[Dict[str, Any]]:
        """Get stored OTP data."""
        return self._otp_storage.get(email)
    
    def _remove_otp(self, email: str) -> None:
        """Remove OTP from storage."""
        self._otp_storage.pop(email, None)
    
    def _mask_email(self, email: str) -> str:
        """Mask email for security in logs."""
        if "@" in email:
            parts = email.split("@")
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        return "***"
    
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


# === Convenience Functions ===

def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Send email using SendGrid service."""
    service = SendGridService()
    return service.send_email(to_email, subject, html_content, plain_content, **kwargs)


def send_otp_email(
    email: str,
    subject: Optional[str] = None,
    template_data: Optional[Dict[str, Any]] = None,
    otp_code: Optional[str] = None
) -> Tuple[bool, str, str]:
    """Send OTP email using SendGrid service."""
    service = SendGridService()
    return service.send_otp_email(email, subject, template_data, otp_code)


def verify_email_otp(email: str, code: str) -> Tuple[bool, str]:
    """Verify email OTP using SendGrid service."""
    service = SendGridService()
    return service.verify_otp(email, code)
