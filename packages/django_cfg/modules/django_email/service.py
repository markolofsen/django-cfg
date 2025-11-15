"""
Auto-configuring Email Service for django_cfg.

This email service automatically configures itself based on the DjangoConfig instance
without requiring manual parameter passing.
"""

import socket
import threading
from smtplib import SMTPException
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ..base import BaseCfgModule
from ..django_logging import get_logger

logger = get_logger("django_cfg.email")


def _notify_telegram_on_email_error(error_msg: str, context: dict = None):
    """Send telegram notification about email sending error."""
    try:
        from ..django_telegram import DjangoTelegram
        DjangoTelegram.send_error(
            error=f"Email Sending Error\n\n{error_msg}",
            context=context
        )
    except Exception as e:
        logger.debug(f"Could not send telegram notification: {e}")


class DjangoEmailService(BaseCfgModule):
    """
    Auto-configuring email service that gets settings from DjangoConfig.

    Usage:
        from django_cfg.modules import DjangoEmailService

        email = DjangoEmailService()
        email.send_simple("Test", "Hello World!", ["user@example.com"])
    """

    def __init__(self):
        """Initialize email service with auto-discovered config."""
        self.config = self.get_config()
        self.email_config = getattr(self.config, 'email', None)

    def _send_in_background(self, func, *args, **kwargs):
        """
        Execute a function in a background thread to avoid blocking.

        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
        """
        def _wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Background email send failed: {e}"
                logger.error(error_msg)

                # Notify telegram about email error
                context = {
                    'error_type': type(e).__name__,
                    'function': func.__name__ if hasattr(func, '__name__') else 'unknown',
                }
                _notify_telegram_on_email_error(str(e), context)

        thread = threading.Thread(target=_wrapper, daemon=True)
        thread.start()

    def _handle_email_sending(self, email_func, *args, **kwargs):
        """
        Wrapper for email sending with proper timeout/exception handling.

        Args:
            email_func: Email sending function to call
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Result of email_func or 0 on timeout/error
        """
        try:
            result = email_func(*args, **kwargs)
            logger.debug(f"Email sent successfully: {email_func.__name__}")
            return result
        except (socket.timeout, TimeoutError) as e:
            logger.warning(f"Email sending timeout: {e}")
            logger.info("Consider checking SMTP server configuration or network connectivity")
            return 0
        except SMTPException as e:
            logger.warning(f"SMTP error during email sending: {e}")
            logger.info("Email service temporarily unavailable")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error during email sending: {e}")
            if not kwargs.get('fail_silently', False):
                raise
            return 0

    def send_simple(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send a simple text email in background thread (non-blocking).

        Args:
            subject: Email subject
            message: Email message (plain text)
            recipient_list: List of recipient email addresses
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        def _do_send():
            self._handle_email_sending(
                send_mail,
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                fail_silently=fail_silently,
            )

        # Always send in background thread to avoid blocking
        self._send_in_background(_do_send)
        return True

    def send_html(
        self,
        subject: str,
        html_message: str,
        recipient_list: List[str],
        text_message: Optional[str] = None,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send an HTML email with optional plain text alternative in background thread (non-blocking).

        Args:
            subject: Email subject
            html_message: HTML email content
            recipient_list: List of recipient email addresses
            text_message: Plain text alternative (auto-generated if not provided)
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        if text_message is None:
            text_message = strip_tags(html_message)

        def _do_send():
            self._handle_email_sending(
                send_mail,
                subject=subject,
                message=text_message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=fail_silently,
            )

        # Always send in background thread to avoid blocking
        self._send_in_background(_do_send)
        return True

    def send_template(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send an email using a Django template in background thread (non-blocking).

        Args:
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context variables
            recipient_list: List of recipient email addresses
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        # Prepare context with auto-added values
        context = self._prepare_template_context(context)

        # Render HTML template
        html_message = render_to_string(f"{template_name}.html", context)

        # Try to render plain text template
        try:
            text_message = render_to_string(f"{template_name}.txt", context)
        except:
            text_message = strip_tags(html_message)

        return self.send_html(
            subject=subject,
            html_message=html_message,
            recipient_list=recipient_list,
            text_message=text_message,
            from_email=from_email,
            fail_silently=fail_silently,
        )

    def send_multipart(
        self,
        subject: str,
        recipient_list: List[str],
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        attachments: Optional[List[tuple]] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send a multipart email with attachments.

        Args:
            subject: Email subject
            recipient_list: List of recipient email addresses
            html_content: HTML email content
            text_content: Plain text email content
            from_email: Sender email (auto-detected if not provided)
            attachments: List of (filename, content, mimetype) tuples
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email was sent successfully, False otherwise
        """
        from_email = self._get_formatted_from_email(from_email)

        if not html_content and not text_content:
            raise ValueError("Either html_content or text_content must be provided")

        def _send_multipart_email():
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content or strip_tags(html_content or ''),
                    from_email=from_email,
                    to=recipient_list,
                )

                if html_content:
                    email.attach_alternative(html_content, "text/html")

                if attachments:
                    for filename, content, mimetype in attachments:
                        email.attach(filename, content, mimetype)

                email.send(fail_silently=fail_silently)
                logger.info(f"Multipart email sent successfully to {recipient_list}")
            except Exception as e:
                error_msg = f"Failed to send multipart email: {e}"
                logger.error(error_msg)

                # Notify telegram about error
                context = {
                    'error_type': type(e).__name__,
                    'subject': subject,
                    'recipients': recipient_list,
                    'from': from_email,
                    'attachments_count': len(attachments) if attachments else 0,
                }
                _notify_telegram_on_email_error(str(e), context)

                if not fail_silently:
                    raise

        # Always send in background thread to avoid blocking
        self._send_in_background(_send_multipart_email)
        return True

    def send_with_attachments(
        self,
        subject: str,
        recipient_list: List[str],
        attachments: List[tuple],
        message: Optional[str] = None,
        html_message: Optional[str] = None,
        template_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Universal method to send emails with attachments.

        Args:
            subject: Email subject
            recipient_list: List of recipient email addresses
            attachments: List of (filename, content, mimetype) tuples
            message: Plain text message (for simple emails)
            html_message: HTML message (for HTML emails)
            template_name: Template name without .html extension (for template emails)
            context: Template context variables (required if template_name provided)
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email was sent successfully, False otherwise
        """
        html_content = None
        text_content = None

        if template_name:
            # Template-based email
            if not context:
                context = {}

            # Prepare context with auto-added values
            context = self._prepare_template_context(context)

            # Render templates
            html_content = render_to_string(f"{template_name}.html", context)
            try:
                text_content = render_to_string(f"{template_name}.txt", context)
            except:
                text_content = strip_tags(html_content)

        elif html_message:
            # HTML email
            html_content = html_message
            text_content = message or strip_tags(html_message)

        elif message:
            # Simple text email
            text_content = message

        else:
            raise ValueError("Must provide either message, html_message, or template_name")

        return self.send_multipart(
            subject=subject,
            recipient_list=recipient_list,
            html_content=html_content,
            text_content=text_content,
            from_email=from_email,
            attachments=attachments,
            fail_silently=fail_silently,
        )

    def _prepare_template_context(self, context: Dict[str, Any], email_log_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Prepare template context with auto-added values from config.

        Args:
            context: Original context dictionary
            email_log_id: Optional email log ID for tracking

        Returns:
            Updated context with auto-added values
        """
        # Create a copy to avoid modifying the original
        updated_context = context.copy()

        # Auto-add project_name from config if not provided
        if 'project_name' not in updated_context:
            updated_context['project_name'] = self.config.project_name

        # Auto-add logo_url from config if not provided
        if 'logo_url' not in updated_context and self.config.project_logo:
            updated_context['logo_url'] = self.config.project_logo

        # Auto-add site_url from config if not provided
        if 'site_url' not in updated_context:
            updated_context['site_url'] = self.config.site_url

        # Add tracking URLs if email_log_id is provided
        if email_log_id:
            base_url = self.config.api_url.rstrip('/')
            updated_context['tracking_pixel_url'] = f"{base_url}/cfg/newsletter/track/open/{email_log_id}/"
            updated_context['tracking_click_url'] = f"{base_url}/cfg/newsletter/track/click/{email_log_id}"

        return updated_context

    def _get_default_from_email(self) -> str:
        """Get the default from email address."""
        if self.email_config and self.email_config.default_from:
            return self.email_config.default_from

        # Fallback to Django settings
        return getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

    def _get_formatted_from_email(self, from_email: Optional[str] = None) -> str:
        """
        Get formatted from email with project name.

        Args:
            from_email: Optional custom from email

        Returns:
            Formatted email in format: "Project Name <email@example.com>"
        """
        if from_email is None:
            from_email = self._get_default_from_email()

        # If email already contains name (has < and >), return as is
        if '<' in from_email and '>' in from_email:
            return from_email

        # Format with project name
        project_name = self.config.project_name
        return f'"{project_name}" <{from_email}>'

    def is_configured(self) -> bool:
        """Check if email is properly configured."""
        return self.email_config is not None and bool(self.email_config.host)

    def get_backend_info(self) -> Dict[str, Any]:
        """Get information about the current email backend."""
        backend = getattr(settings, 'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

        info = {
            'backend': backend,
            'configured': self.is_configured(),
            'host': getattr(settings, 'EMAIL_HOST', None),
            'port': getattr(settings, 'EMAIL_PORT', None),
            'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
            'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
        }

        if self.email_config:
            info.update({
                'default_from_email': self.email_config.default_from,
                'default_from_name': getattr(self.email_config, 'default_from_name', None),
            })

        return info

    # Backward compatibility aliases
    def send_html_with_attachments(self, subject: str, html_message: str, recipient_list: List[str],
                                 attachments: List[tuple], text_message: Optional[str] = None,
                                 from_email: Optional[str] = None, fail_silently: bool = False) -> bool:
        """Alias for send_with_attachments with HTML message."""
        return self.send_with_attachments(
            subject=subject, recipient_list=recipient_list, attachments=attachments,
            html_message=html_message, message=text_message, from_email=from_email, fail_silently=fail_silently
        )

    def send_template_with_attachments(self, subject: str, template_name: str, context: Dict[str, Any],
                                     recipient_list: List[str], attachments: List[tuple],
                                     from_email: Optional[str] = None, fail_silently: bool = False) -> bool:
        """Alias for send_with_attachments with template."""
        return self.send_with_attachments(
            subject=subject, recipient_list=recipient_list, attachments=attachments,
            template_name=template_name, context=context, from_email=from_email, fail_silently=fail_silently
        )

    def send_template_with_tracking(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        email_log_id: str,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Send an email using a Django template with tracking support in background thread (non-blocking).

        Args:
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context variables
            recipient_list: List of recipient email addresses
            email_log_id: Email log ID for tracking
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors

        Returns:
            True if email queued successfully
        """
        from_email = self._get_formatted_from_email(from_email)

        # Prepare context with auto-added values and tracking
        context = self._prepare_template_context(context, email_log_id)

        # Render HTML template
        html_message = render_to_string(f"{template_name}.html", context)

        # Try to render plain text template
        try:
            text_message = render_to_string(f"{template_name}.txt", context)
        except:
            text_message = strip_tags(html_message)

        return self.send_html(
            subject=subject,
            html_message=html_message,
            recipient_list=recipient_list,
            text_message=text_message,
            from_email=from_email,
            fail_silently=fail_silently,
        )


__all__ = ["DjangoEmailService"]
