"""
Email service for newsletter application.

Uses the built-in DjangoEmailService for sending emails with proper logging.
"""

import logging
from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from django.utils import timezone

from django_cfg.modules.django_email import DjangoEmailService
from ..models import Newsletter, NewsletterSubscription, EmailLog

User = get_user_model()
logger = logging.getLogger(__name__)


class NewsletterEmailService:
    """Email service for newsletter application using DjangoEmailService."""
    
    def __init__(self):
        """Initialize the email service."""
        self.email_service = DjangoEmailService()
    
    def _create_email_log(
        self, 
        recipient: str, 
        subject: str, 
        status: str, 
        newsletter: Optional[Newsletter] = None,
        campaign = None
    ) -> EmailLog:
        """
        Create email log entry for sent email.
        
        Args:
            recipient: Recipient email
            subject: Email subject
            status: Email status (sent/failed)
            newsletter: Newsletter instance (optional)
            campaign: NewsletterCampaign instance (optional)
            
        Returns:
            Created EmailLog instance
        """
        try:
            from django.utils import timezone
            
            # Try to find user by email
            user = None
            try:
                user = User.objects.get(email=recipient)
            except User.DoesNotExist:
                pass
            
            log_data = {
                'user': user,
                'newsletter': newsletter,
                'campaign': campaign,
                'recipient': recipient,
                'subject': subject,
                'status': status,
                'body': f"Newsletter email sent via campaign"
            }
            
            # Add sent_at for successful emails
            if status == EmailLog.EmailLogStatus.SENT:
                log_data['sent_at'] = timezone.now()
            
            return EmailLog.objects.create(**log_data)
        except Exception as e:
            logger.error(f"Failed to create email log: {e}")
            raise
    
    def send_newsletter_email(
        self,
        newsletter: Newsletter,
        subject: str,
        email_title: str,
        main_text: str,
        main_html_content: str = "",
        button_text: str = "",
        button_url: str = "",
        secondary_text: str = "",
        attachments: Optional[List[tuple]] = None,
        send_to_all: bool = False,
        specific_emails: Optional[List[str]] = None,
        campaign = None
    ) -> Dict[str, Any]:
        """
        Send newsletter email to subscribers.
        
        Args:
            newsletter: Newsletter instance
            subject: Email subject
            email_title: Title for the email
            main_text: Main text content
            main_html_content: Additional HTML content
            button_text: Button text (optional)
            button_url: Button URL (optional)
            secondary_text: Secondary text (optional)
            attachments: List of (filename, content, mimetype) tuples (optional)
            send_to_all: Send to all active subscribers
            specific_emails: List of specific emails to send to
            
        Returns:
            Dictionary with sending results
        """
        try:
            # Get recipient emails
            if send_to_all:
                emails = list(
                    NewsletterSubscription.objects.filter(
                        newsletter=newsletter,
                        is_active=True
                    ).values_list('email', flat=True)
                )
            elif specific_emails:
                # Validate that emails are subscribed to this newsletter
                valid_emails = list(
                    NewsletterSubscription.objects.filter(
                        newsletter=newsletter,
                        email__in=specific_emails,
                        is_active=True
                    ).values_list('email', flat=True)
                )
                emails = valid_emails
            else:
                return {
                    'success': False,
                    'error': 'No recipients specified',
                    'sent_count': 0,
                    'failed_count': 0
                }
            
            if not emails:
                return {
                    'success': False,
                    'error': 'No valid recipients found',
                    'sent_count': 0,
                    'failed_count': 0
                }
            
            # Use the optimized send_bulk_email method with tracking
            result = self.send_bulk_email(
                recipients=emails,
                subject=subject,
                email_title=email_title,
                main_text=main_text,
                main_html_content=main_html_content,
                button_text=button_text,
                button_url=button_url,
                secondary_text=secondary_text,
                attachments=attachments,
                enable_tracking=True,
                newsletter=newsletter,
                campaign=campaign
            )
            
            # Add newsletter-specific context to the result
            result.update({
                'newsletter_id': newsletter.id,
                'newsletter_title': newsletter.title
            })
            
            logger.info(f"Newsletter '{newsletter.title}' sent to {len(emails)} recipients, {result['sent_count']} successful")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to send newsletter emails: {e}")
            return {
                'success': False,
                'error': str(e),
                'sent_count': 0,
                'failed_count': 0
            }
    
    def send_subscription_welcome_email(self, subscription: NewsletterSubscription) -> bool:
        """
        Send welcome email to new newsletter subscriber.
        
        Args:
            subscription: NewsletterSubscription instance
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            context = {
                'email_title': f"Welcome to {subscription.newsletter.title}",
                'greeting': f"Hello",
                'main_text': f"Thank you for subscribing to our newsletter <strong>{subscription.newsletter.title}</strong>!",
                'main_html_content': f"""
                    <p>You'll receive updates and news directly to your inbox at <strong>{subscription.email}</strong>.</p>
                    <p>We're excited to have you as part of our community!</p>
                    {f'<p><strong>About this newsletter:</strong> {subscription.newsletter.description}</p>' if subscription.newsletter.description else ''}
                """,
                'secondary_text': f'If you no longer wish to receive these emails, you can <a href="/mailer/unsubscribe/{subscription.id}/">unsubscribe here</a>.'
            }
            
            self.email_service.send_template(
                subject=f"Welcome to {subscription.newsletter.title}",
                template_name="emails/base_email",
                context=context,
                recipient_list=[subscription.email],
                fail_silently=False
            )
            
            logger.info(f"Welcome email sent to {subscription.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {subscription.email}: {e}")
            return False
    
    def send_unsubscribe_confirmation_email(self, subscription: NewsletterSubscription) -> bool:
        """
        Send unsubscribe confirmation email.
        
        Args:
            subscription: NewsletterSubscription instance
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            context = {
                'email_title': "Unsubscribe Confirmation",
                'greeting': f"Hello",
                'main_text': f"You have been successfully unsubscribed from <strong>{subscription.newsletter.title}</strong>.",
                'main_html_content': f"""
                    <p>Your email address <strong>{subscription.email}</strong> will no longer receive emails from this newsletter.</p>
                    <p>If this was a mistake, you can resubscribe at any time by visiting our website.</p>
                    <p>We're sorry to see you go!</p>
                """
            }
            
            self.email_service.send_template(
                subject=f"Unsubscribed from {subscription.newsletter.title}",
                template_name="emails/base_email",
                context=context,
                recipient_list=[subscription.email],
                fail_silently=False
            )
            
            logger.info(f"Unsubscribe confirmation sent to {subscription.email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send unsubscribe confirmation to {subscription.email}: {e}")
            return False
    
    def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        email_title: str,
        main_text: str,
        main_html_content: str = "",
        button_text: str = "",
        button_url: str = "",
        secondary_text: str = "",
        attachments: Optional[List[tuple]] = None,
        enable_tracking: bool = True,
        newsletter: Optional[Newsletter] = None,
        campaign = None
    ) -> Dict[str, Any]:
        """
        Send bulk email using base_email template with optional attachments and tracking.
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            email_title: Title for the email
            main_text: Main text content
            main_html_content: Additional HTML content
            button_text: Button text (optional)
            button_url: Button URL (optional)
            secondary_text: Secondary text (optional)
            attachments: List of (filename, content, mimetype) tuples (optional)
            enable_tracking: Enable email tracking (default: True)
            newsletter: Newsletter instance for logging (optional)
            campaign: Campaign instance for logging (optional)
            
        Returns:
            Dictionary with sending results
        """
        sent_count = 0
        failed_count = 0
        
        try:
            for recipient in recipients:
                try:
                    # Create email log first to get ID for tracking
                    email_log = None
                    if enable_tracking:
                        email_log = self._create_email_log(
                            recipient=recipient,
                            subject=subject,
                            status=EmailLog.EmailLogStatus.PENDING,
                            newsletter=newsletter,
                            campaign=campaign
                        )
                    
                    context = {
                        'email_title': email_title,
                        'greeting': "Hello",
                        'main_text': main_text,
                        'main_html_content': main_html_content,
                        'button_text': button_text,
                        'button_url': button_url,
                        'secondary_text': secondary_text
                    }
                    
                    # Send email with tracking if enabled
                    if enable_tracking and email_log:
                        success = self.email_service.send_template_with_tracking(
                            subject=subject,
                            template_name="emails/base_email",
                            context=context,
                            recipient_list=[recipient],
                            email_log_id=str(email_log.id),
                            fail_silently=False
                        )
                        success = success > 0
                    else:
                        # Send without tracking
                        if attachments:
                            success = self.email_service.send_with_attachments(
                                subject=subject,
                                recipient_list=[recipient],
                                attachments=attachments,
                                template_name="emails/base_email",
                                context=context,
                                fail_silently=False
                            )
                        else:
                            success = self.email_service.send_template(
                                subject=subject,
                                template_name="emails/base_email",
                                context=context,
                                recipient_list=[recipient],
                                fail_silently=False
                            ) > 0
                    
                    # Update email log status
                    if enable_tracking and email_log:
                        if success:
                            email_log.status = EmailLog.EmailLogStatus.SENT
                            email_log.sent_at = timezone.now()
                            sent_count += 1
                        else:
                            email_log.status = EmailLog.EmailLogStatus.FAILED
                            failed_count += 1
                        email_log.save()
                    else:
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1
                            
                except Exception as e:
                    logger.error(f"Failed to send email to {recipient}: {e}")
                    failed_count += 1
                    
                    # Update email log if exists
                    if enable_tracking and email_log:
                        email_log.status = EmailLog.EmailLogStatus.FAILED
                        email_log.error_message = str(e)
                        email_log.save()
            
            logger.info(f"Bulk email sent to {len(recipients)} recipients, {sent_count} successful")
            
            return {
                'success': sent_count > 0,
                'sent_count': sent_count,
                'failed_count': failed_count,
                'total_recipients': len(recipients)
            }
            
        except Exception as e:
            logger.error(f"Failed to send bulk emails: {e}")
            return {
                'success': False,
                'error': str(e),
                'sent_count': sent_count,
                'failed_count': len(recipients) - sent_count
            }
