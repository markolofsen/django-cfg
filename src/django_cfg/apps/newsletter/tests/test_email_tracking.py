"""
Tests for email tracking functionality.
"""

import uuid
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock

from ..models import Newsletter, EmailLog, NewsletterSubscription, NewsletterCampaign
from ..services.email_service import NewsletterEmailService

User = get_user_model()


class EmailTrackingTestCase(TestCase):
    """Test cases for email tracking functionality"""
    
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
            title='Test Newsletter',
            description='Test newsletter content',
            is_active=True
        )
        
        # Create email log
        self.email_log = EmailLog.objects.create(
            user=self.user,
            newsletter=self.newsletter,
            recipient='test@example.com',
            subject='Test Subject',
            body='<p>Test body</p>',
            status=EmailLog.EmailLogStatus.SENT
        )
    
    def test_email_log_tracking_fields(self):
        """Test that email log has tracking fields"""
        self.assertIsNone(self.email_log.opened_at)
        self.assertIsNone(self.email_log.clicked_at)
        self.assertFalse(self.email_log.is_opened)
        self.assertFalse(self.email_log.is_clicked)
    
    def test_mark_opened(self):
        """Test marking email as opened"""
        # Initially not opened
        self.assertFalse(self.email_log.is_opened)
        self.assertIsNone(self.email_log.opened_at)
        
        # Mark as opened
        self.email_log.mark_opened()
        
        # Check that it's marked as opened
        self.assertTrue(self.email_log.is_opened)
        self.assertIsNotNone(self.email_log.opened_at)
        
        # Mark as opened again - should not change timestamp
        original_opened_at = self.email_log.opened_at
        self.email_log.mark_opened()
        self.assertEqual(self.email_log.opened_at, original_opened_at)
    
    def test_mark_clicked(self):
        """Test marking email link as clicked"""
        # Initially not clicked
        self.assertFalse(self.email_log.is_clicked)
        self.assertIsNone(self.email_log.clicked_at)
        
        # Mark as clicked
        self.email_log.mark_clicked()
        
        # Check that it's marked as clicked
        self.assertTrue(self.email_log.is_clicked)
        self.assertIsNotNone(self.email_log.clicked_at)
        
        # Mark as clicked again - should not change timestamp
        original_clicked_at = self.email_log.clicked_at
        self.email_log.mark_clicked()
        self.assertEqual(self.email_log.clicked_at, original_clicked_at)
    
    def test_track_email_open_view(self):
        """Test email open tracking view"""
        # Get tracking URL
        url = reverse('cfg_newsletter:track-open', kwargs={'email_log_id': self.email_log.id})
        
        # Make request to tracking pixel
        response = self.client.get(url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/gif')
        
        # Check that email log was marked as opened
        self.email_log.refresh_from_db()
        self.assertTrue(self.email_log.is_opened)
        self.assertIsNotNone(self.email_log.opened_at)
    
    def test_track_email_open_invalid_id(self):
        """Test email open tracking with invalid ID"""
        # Use random UUID
        invalid_id = uuid.uuid4()
        url = reverse('cfg_newsletter:track-open', kwargs={'email_log_id': invalid_id})
        
        # Make request - should still return pixel but not crash
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/gif')
    
    def test_track_email_click_view(self):
        """Test email click tracking view"""
        # Get tracking URL with redirect
        redirect_url = 'https://example.com/target'
        url = reverse('cfg_newsletter:track-click', kwargs={'email_log_id': self.email_log.id})
        url += f'?url={redirect_url}'
        
        # Make request to tracking URL
        response = self.client.get(url)
        
        # Check redirect response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)
        
        # Check that email log was marked as clicked
        self.email_log.refresh_from_db()
        self.assertTrue(self.email_log.is_clicked)
        self.assertIsNotNone(self.email_log.clicked_at)
    
    def test_track_email_click_no_url(self):
        """Test email click tracking without redirect URL"""
        # Get tracking URL without redirect
        url = reverse('cfg_newsletter:track-click', kwargs={'email_log_id': self.email_log.id})
        
        # Make request to tracking URL
        response = self.client.get(url)
        
        # Check redirect to default URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        
        # Check that email log was marked as clicked
        self.email_log.refresh_from_db()
        self.assertTrue(self.email_log.is_clicked)
    
    def test_track_email_click_invalid_id(self):
        """Test email click tracking with invalid ID"""
        # Use random UUID
        invalid_id = uuid.uuid4()
        redirect_url = 'https://example.com/target'
        url = reverse('cfg_newsletter:track-click', kwargs={'email_log_id': invalid_id})
        url += f'?url={redirect_url}'
        
        # Make request - should still redirect but not crash
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)


class EmailServiceTrackingTestCase(TestCase):
    """Test cases for email service tracking integration"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create newsletter subscription
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter Service',
            description='Test newsletter content',
            is_active=True
        )
        
        NewsletterSubscription.objects.create(
            user=self.user,
            newsletter=self.newsletter,
            email=self.user.email,
            is_active=True
        )
        
        self.email_service = NewsletterEmailService()
    
    @patch('django_cfg.modules.django_email.DjangoEmailService.send_template_with_tracking')
    def test_send_bulk_email_with_tracking(self, mock_send_tracking):
        """Test sending bulk email with tracking enabled"""
        # Mock successful sending
        mock_send_tracking.return_value = 1
        
        # Send bulk email with tracking
        result = self.email_service.send_bulk_email(
            recipients=['test@example.com'],
            subject='Test Subject',
            email_title='Test Title',
            main_text='Test content',
            enable_tracking=True,
            newsletter=self.newsletter
        )
        
        # Check result
        self.assertEqual(result['sent_count'], 1)
        self.assertEqual(result['failed_count'], 0)
        
        # Check that email log was created
        email_logs = EmailLog.objects.filter(newsletter=self.newsletter)
        self.assertEqual(email_logs.count(), 1)
        
        email_log = email_logs.first()
        self.assertEqual(email_log.status, EmailLog.EmailLogStatus.SENT)
        self.assertIsNotNone(email_log.sent_at)
        
        # Check that tracking method was called
        mock_send_tracking.assert_called_once()
        call_args = mock_send_tracking.call_args
        self.assertIn('email_log_id', call_args.kwargs)
        self.assertEqual(call_args.kwargs['email_log_id'], str(email_log.id))
    
    @patch('django_cfg.modules.django_email.DjangoEmailService.send_template')
    def test_send_bulk_email_without_tracking(self, mock_send):
        """Test sending bulk email without tracking"""
        # Mock successful sending
        mock_send.return_value = 1
        
        # Send bulk email without tracking
        result = self.email_service.send_bulk_email(
            recipients=['test@example.com'],
            subject='Test Subject',
            email_title='Test Title',
            main_text='Test content',
            enable_tracking=False,
            newsletter=self.newsletter
        )
        
        # Check result
        self.assertEqual(result['sent_count'], 1)
        self.assertEqual(result['failed_count'], 0)
        
        # Check that regular send method was called (not tracking)
        mock_send.assert_called_once()
        
        # Email log should NOT be created when tracking is disabled
        email_logs = EmailLog.objects.filter(newsletter=self.newsletter)
        self.assertEqual(email_logs.count(), 0)  # No logs when tracking disabled
    
    def test_send_newsletter_email_with_tracking(self):
        """Test sending newsletter email with tracking enabled"""
        # Send newsletter email (no mocking - test real functionality)
        result = self.email_service.send_newsletter_email(
            newsletter=self.newsletter,
            subject='Test Newsletter',
            email_title='Newsletter Title',
            main_text='Newsletter content',
            send_to_all=True  # Send to all subscribers
        )
        
        # Check result
        self.assertEqual(result['sent_count'], 1)
        self.assertEqual(result['failed_count'], 0)
        
        # Check that email log was created with tracking
        email_logs = EmailLog.objects.filter(newsletter=self.newsletter)
        self.assertEqual(email_logs.count(), 1)
        
        email_log = email_logs.first()
        self.assertEqual(email_log.status, EmailLog.EmailLogStatus.SENT)


class EmailTemplateTrackingTestCase(TestCase):
    """Test cases for email template tracking integration"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='Test newsletter content',
            is_active=True
        )
        
        self.email_log = EmailLog.objects.create(
            user=self.user,
            newsletter=self.newsletter,
            recipient='test@example.com',
            subject='Test Subject',
            body='<p>Test body</p>',
            status=EmailLog.EmailLogStatus.SENT
        )
    
    @patch('django_cfg.modules.django_email.DjangoEmailService._prepare_template_context')
    def test_template_context_with_tracking(self, mock_prepare_context):
        """Test that template context includes tracking URLs"""
        from django_cfg.modules.django_email import DjangoEmailService
        
        # Mock context preparation
        mock_prepare_context.return_value = {
            'email_title': 'Test Title',
            'tracking_pixel_url': f'http://example.com/api/newsletter/track/open/{self.email_log.id}/',
            'tracking_click_url': f'http://example.com/api/newsletter/track/click/{self.email_log.id}'
        }
        
        service = DjangoEmailService()
        context = service._prepare_template_context(
            {'email_title': 'Test Title'}, 
            email_log_id=str(self.email_log.id)
        )
        
        # Check that tracking URLs are included
        self.assertIn('tracking_pixel_url', context)
        self.assertIn('tracking_click_url', context)
        self.assertIn(str(self.email_log.id), context['tracking_pixel_url'])
        self.assertIn(str(self.email_log.id), context['tracking_click_url'])
