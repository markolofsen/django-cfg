import threading
import time
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Newsletter, EmailLog
# NewsletterManager is no longer used - tests updated to reflect current architecture

User = get_user_model()


class NewsletterManagerTestCase(TestCase):
    """Test cases for Newsletter model functionality"""
    
    def setUp(self):
        """Set up test data"""
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=True,
        )
        
        # Create test newsletter
        self.newsletter = Newsletter.objects.create(
            title='Test Newsletter',
            description='Test newsletter content',
            is_active=True
        )
    
    def test_newsletter_creation(self):
        """Test newsletter creation"""
        self.assertEqual(self.newsletter.title, 'Test Newsletter')
        self.assertEqual(self.newsletter.description, 'Test newsletter content')
        self.assertTrue(self.newsletter.is_active)
    
    def test_newsletter_filtering(self):
        """Test newsletter filtering by active status"""
        # Create inactive newsletter
        inactive_newsletter = Newsletter.objects.create(
            title='Inactive Newsletter',
            description='Inactive content',
            is_active=False
        )
        
        active_newsletters = Newsletter.objects.filter(is_active=True)
        self.assertEqual(active_newsletters.count(), 1)
        self.assertEqual(active_newsletters.first(), self.newsletter)
    
    def test_newsletter_str_representation(self):
        """Test newsletter string representation"""
        # Newsletter model __str__ method returns just the title
        self.assertEqual(str(self.newsletter), self.newsletter.title)
    
    def test_newsletter_ordering(self):
        """Test newsletter ordering by creation date"""
        # Create another newsletter
        newer_newsletter = Newsletter.objects.create(
            title='Newer Newsletter',
            description='Newer content',
            is_active=True
        )
        
        newsletters = list(Newsletter.objects.all())
        # Should be ordered by created_at descending
        self.assertEqual(newsletters[0], newer_newsletter)
        self.assertEqual(newsletters[1], self.newsletter)
    
    def test_newsletter_meta_options(self):
        """Test newsletter model meta options"""
        meta = Newsletter._meta
        
        self.assertEqual(meta.verbose_name, 'Newsletter')
        self.assertEqual(meta.verbose_name_plural, 'Newsletters')
        self.assertEqual(meta.ordering, ['-created_at'])
    
    
    
    