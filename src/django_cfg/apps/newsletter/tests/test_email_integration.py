"""
Integration tests for email tracking functionality.
"""

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from unittest.mock import patch

from ..models import Newsletter, EmailLog, NewsletterSubscription
from ..services.email_service import NewsletterEmailService

User = get_user_model()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailTrackingIntegrationTestCase(TestCase):
    """Integration tests for email tracking with real email sending"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create test newsletter
        self.newsletter = Newsletter.objects.create(
            title='Integration Test Newsletter',
            description='Test newsletter for integration testing',
            is_active=True
        )
        
        # Create newsletter subscription
        NewsletterSubscription.objects.create(
            user=self.user,
            newsletter=self.newsletter,
            email=self.user.email,  # Add email field
            is_active=True
        )
        
        self.email_service = NewsletterEmailService()
    
    def test_send_email_with_tracking_creates_log(self):
        """Test that sending email with tracking creates EmailLog"""
        # Clear any existing mail
        mail.outbox = []
        
        # Send email with tracking
        result = self.email_service.send_bulk_email(
            recipients=['test@example.com'],
            subject='Test Email with Tracking',
            email_title='Test Title',
            main_text='This is a test email with tracking enabled.',
            button_text='Click Me',
            button_url='https://example.com/test',
            enable_tracking=True,
            newsletter=self.newsletter
        )
        
        # Check result
        self.assertEqual(result['sent_count'], 1)
        self.assertEqual(result['failed_count'], 0)
        
        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ['test@example.com'])
        self.assertEqual(sent_email.subject, 'Test Email with Tracking')
        
        # Check that EmailLog was created
        email_logs = EmailLog.objects.filter(newsletter=self.newsletter)
        self.assertEqual(email_logs.count(), 1)
        
        email_log = email_logs.first()
        self.assertEqual(email_log.recipient, 'test@example.com')
        self.assertEqual(email_log.status, EmailLog.EmailLogStatus.SENT)
        self.assertIsNotNone(email_log.sent_at)
        
        # Check HTML version for tracking (tracking is only in HTML version)
        self.assertTrue(hasattr(sent_email, 'alternatives') and sent_email.alternatives, 
                       "Email should have HTML alternative for tracking")
        
        html_body = sent_email.alternatives[0][0]
        self.assertIn('track/open/', html_body)  # Tracking pixel URL
        self.assertIn('track/click/', html_body)  # Click tracking URL
        self.assertIn(str(email_log.id), html_body)  # Tracking ID should be in HTML
    
    def test_tracking_pixel_marks_email_as_opened(self):
        """Test that accessing tracking pixel marks email as opened"""
        # First send an email to create EmailLog
        result = self.email_service.send_bulk_email(
            recipients=['test@example.com'],
            subject='Test Email',
            email_title='Test',
            main_text='Test content',
            enable_tracking=True,
            newsletter=self.newsletter
        )
        
        # Get the created EmailLog
        email_log = EmailLog.objects.filter(newsletter=self.newsletter).first()
        self.assertIsNotNone(email_log)
        self.assertFalse(email_log.is_opened)
        
        # Access tracking pixel
        tracking_url = reverse('cfg_newsletter:track-open', kwargs={'email_log_id': email_log.id})
        response = self.client.get(tracking_url)
        
        # Check response is a valid image
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/gif')
        
        # Check that email is marked as opened
        email_log.refresh_from_db()
        self.assertTrue(email_log.is_opened)
        self.assertIsNotNone(email_log.opened_at)
    
    def test_click_tracking_marks_email_as_clicked(self):
        """Test that click tracking marks email as clicked and redirects"""
        # First send an email to create EmailLog
        result = self.email_service.send_bulk_email(
            recipients=['test@example.com'],
            subject='Test Email',
            email_title='Test',
            main_text='Test content',
            button_text='Click Here',
            button_url='https://example.com/destination',
            enable_tracking=True,
            newsletter=self.newsletter
        )
        
        # Get the created EmailLog
        email_log = EmailLog.objects.filter(newsletter=self.newsletter).first()
        self.assertIsNotNone(email_log)
        self.assertFalse(email_log.is_clicked)
        
        # Access click tracking URL
        tracking_url = reverse('cfg_newsletter:track-click', kwargs={'email_log_id': email_log.id})
        tracking_url += '?url=https://example.com/destination'
        
        response = self.client.get(tracking_url)
        
        # Check redirect response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://example.com/destination')
        
        # Check that email is marked as clicked
        email_log.refresh_from_db()
        self.assertTrue(email_log.is_clicked)
        self.assertIsNotNone(email_log.clicked_at)
    
    def test_newsletter_email_sending_with_tracking(self):
        """Test complete newsletter sending workflow with tracking"""
        # Clear any existing mail from signals
        mail.outbox = []
        
        # Send newsletter email
        result = self.email_service.send_newsletter_email(
            newsletter=self.newsletter,
            subject='Newsletter Test',
            email_title='Monthly Newsletter',
            main_text='This is our monthly newsletter content.',
            button_text='Read More',
            button_url='https://example.com/newsletter',
            send_to_all=True  # Send to all subscribers
        )
        
        # Check result
        self.assertEqual(result['sent_count'], 1)  # One subscriber
        self.assertEqual(result['failed_count'], 0)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        # Check EmailLog was created with tracking
        email_logs = EmailLog.objects.filter(newsletter=self.newsletter)
        self.assertEqual(email_logs.count(), 1)
        
        email_log = email_logs.first()
        self.assertEqual(email_log.status, EmailLog.EmailLogStatus.SENT)
        
        # Test tracking functionality
        # 1. Test open tracking
        open_url = reverse('cfg_newsletter:track-open', kwargs={'email_log_id': email_log.id})
        open_response = self.client.get(open_url)
        self.assertEqual(open_response.status_code, 200)
        
        # 2. Test click tracking
        click_url = reverse('cfg_newsletter:track-click', kwargs={'email_log_id': email_log.id})
        click_url += '?url=https://example.com/newsletter'
        click_response = self.client.get(click_url)
        self.assertEqual(click_response.status_code, 302)
        
        # Verify tracking was recorded
        email_log.refresh_from_db()
        self.assertTrue(email_log.is_opened)
        self.assertTrue(email_log.is_clicked)
        self.assertIsNotNone(email_log.opened_at)
        self.assertIsNotNone(email_log.clicked_at)
    
    def test_multiple_opens_only_record_first_time(self):
        """Test that multiple opens only record the first timestamp"""
        # Send email
        result = self.email_service.send_bulk_email(
            recipients=['test@example.com'],
            subject='Test Email',
            email_title='Test',
            main_text='Test content',
            enable_tracking=True,
            newsletter=self.newsletter
        )
        
        email_log = EmailLog.objects.filter(newsletter=self.newsletter).first()
        
        # First open
        open_url = reverse('cfg_newsletter:track-open', kwargs={'email_log_id': email_log.id})
        self.client.get(open_url)
        
        email_log.refresh_from_db()
        first_opened_at = email_log.opened_at
        self.assertIsNotNone(first_opened_at)
        
        # Second open (should not change timestamp)
        self.client.get(open_url)
        
        email_log.refresh_from_db()
        self.assertEqual(email_log.opened_at, first_opened_at)
    
    def test_tracking_with_invalid_email_log_id(self):
        """Test tracking with invalid email log ID handles gracefully"""
        import uuid
        
        # Test open tracking with invalid ID
        invalid_id = uuid.uuid4()
        open_url = reverse('cfg_newsletter:track-open', kwargs={'email_log_id': invalid_id})
        open_response = self.client.get(open_url)
        
        # Should still return tracking pixel
        self.assertEqual(open_response.status_code, 200)
        self.assertEqual(open_response['Content-Type'], 'image/gif')
        
        # Test click tracking with invalid ID
        click_url = reverse('cfg_newsletter:track-click', kwargs={'email_log_id': invalid_id})
        click_url += '?url=https://example.com/test'
        click_response = self.client.get(click_url)
        
        # Should still redirect
        self.assertEqual(click_response.status_code, 302)
        self.assertEqual(click_response.url, 'https://example.com/test')
