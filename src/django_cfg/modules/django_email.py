"""
Auto-configuring Email Service for django_cfg.

This email service automatically configures itself based on the DjangoConfig instance
without requiring manual parameter passing.
"""

from typing import List, Optional, Dict, Any, Union
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from . import BaseModule


class DjangoEmailService(BaseModule):
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
    
    def send_simple(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> int:
        """
        Send a simple text email.
        
        Args:
            subject: Email subject
            message: Email message (plain text)
            recipient_list: List of recipient email addresses
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors
            
        Returns:
            Number of emails sent successfully
        """
        if from_email is None:
            from_email = self._get_default_from_email()
        
        return send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=fail_silently,
        )
    
    def send_html(
        self,
        subject: str,
        html_message: str,
        recipient_list: List[str],
        text_message: Optional[str] = None,
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> int:
        """
        Send an HTML email with optional plain text alternative.
        
        Args:
            subject: Email subject
            html_message: HTML email content
            recipient_list: List of recipient email addresses
            text_message: Plain text alternative (auto-generated if not provided)
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors
            
        Returns:
            Number of emails sent successfully
        """
        if from_email is None:
            from_email = self._get_default_from_email()
        
        if text_message is None:
            text_message = strip_tags(html_message)
        
        return send_mail(
            subject=subject,
            message=text_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=fail_silently,
        )
    
    def send_template(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False,
    ) -> int:
        """
        Send an email using a Django template.
        
        Args:
            subject: Email subject
            template_name: Template name (without .html extension)
            context: Template context variables
            recipient_list: List of recipient email addresses
            from_email: Sender email (auto-detected if not provided)
            fail_silently: Whether to fail silently on errors
            
        Returns:
            Number of emails sent successfully
        """
        if from_email is None:
            from_email = self._get_default_from_email()
        
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
        if from_email is None:
            from_email = self._get_default_from_email()
        
        if not html_content and not text_content:
            raise ValueError("Either html_content or text_content must be provided")
        
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
            return True
            
        except Exception as e:
            if not fail_silently:
                raise e
            return False
    
    def _get_default_from_email(self) -> str:
        """Get the default from email address."""
        if self.email_config and self.email_config.default_from_email:
            return self.email_config.default_from_email
        
        # Fallback to Django settings
        return getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
    
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
                'default_from_email': self.email_config.default_from_email,
                'default_from_name': getattr(self.email_config, 'default_from_name', None),
            })
        
        return info


# Convenience function for quick access
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


# Export public API
__all__ = ['DjangoEmailService', 'send_email']
