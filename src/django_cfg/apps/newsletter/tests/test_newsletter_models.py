from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch

from ..models import Newsletter, EmailLog
# NewsletterManager is no longer used

User = get_user_model()


class NewsletterModelTestCase(TestCase):
    """Test cases for Newsletter model with custom manager"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create test newsletters
        self.active_newsletter = Newsletter.objects.create(
            title='Active Newsletter',
            description='Active content',
            is_active=True
        )
        
        self.inactive_newsletter = Newsletter.objects.create(
            title='Inactive Newsletter',
            description='Inactive content',
            is_active=False
        )
    
    def test_newsletter_str_representation(self):
        """Test string representation of newsletter"""
        # Newsletter model __str__ method returns just the title
        self.assertEqual(
            str(self.active_newsletter),
            self.active_newsletter.title
        )
    
    def test_newsletter_default_active_status(self):
        """Test that new newsletter is active by default"""
        newsletter = Newsletter.objects.create(
            title='New Newsletter',
            description='New content'
        )
        self.assertTrue(newsletter.is_active)
    
    def test_newsletter_active_field(self):
        """Test newsletter active field"""
        self.assertTrue(self.active_newsletter.is_active)
        self.assertFalse(self.inactive_newsletter.is_active)
    
    def test_newsletter_ordering(self):
        """Test that newsletters are ordered by created_at descending"""
        newsletters = list(Newsletter.objects.all())
        
        # Check that newsletters are ordered by created_at descending
        for i in range(len(newsletters) - 1):
            self.assertGreaterEqual(
                newsletters[i].created_at,
                newsletters[i + 1].created_at
            )
    
    def test_newsletter_creation_fields(self):
        """Test newsletter creation with required fields"""
        newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='Test content'
        )
        self.assertEqual(newsletter.title, 'Test Newsletter')
        self.assertEqual(newsletter.description, 'Test content')
        self.assertTrue(newsletter.is_active)  # Default value
    
    def test_newsletter_filtering(self):
        """Test newsletter filtering by active status"""
        active_newsletters = Newsletter.objects.filter(is_active=True)
        inactive_newsletters = Newsletter.objects.filter(is_active=False)
        
        self.assertEqual(active_newsletters.count(), 1)
        self.assertEqual(inactive_newsletters.count(), 1)
        self.assertIn(self.active_newsletter, active_newsletters)
        self.assertIn(self.inactive_newsletter, inactive_newsletters)
    
    def test_newsletter_meta_options(self):
        """Test newsletter model meta options"""
        meta = Newsletter._meta
        
        self.assertEqual(meta.verbose_name, 'Newsletter')
        self.assertEqual(meta.verbose_name_plural, 'Newsletters')
        self.assertEqual(meta.ordering, ['-created_at'])


class NewsletterEmailLogRelationshipTestCase(TestCase):
    """Test relationship between Newsletter and EmailLog"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            is_active=True
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            is_active=True
        )
        
        # Create test newsletter
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='Test newsletter content',
            is_active=True
        )
    
    def test_newsletter_email_logs_relationship(self):
        """Test relationship between Newsletter and EmailLog"""
        # Create email logs for the newsletter
        EmailLog.objects.create(
            user=self.user1,
            newsletter=self.newsletter,
            recipient='user1@example.com',
            subject='Test Subject',
            body='<p>Test body</p>',
            status=EmailLog.EmailLogStatus.SENT
        )
        
        EmailLog.objects.create(
            user=self.user2,
            newsletter=self.newsletter,
            recipient='user2@example.com',
            subject='Test Subject',
            body='<p>Test body</p>',
            status=EmailLog.EmailLogStatus.SENT
        )
        
        # Check that newsletter has email logs
        self.assertEqual(self.newsletter.email_logs.count(), 2)
        
        # Check that we can access email logs through newsletter
        email_logs = list(self.newsletter.email_logs.all())
        self.assertEqual(len(email_logs), 2)
        
        # Check email log details (order may vary)
        users_in_logs = {log.user for log in email_logs}
        self.assertIn(self.user1, users_in_logs)
        self.assertIn(self.user2, users_in_logs) 