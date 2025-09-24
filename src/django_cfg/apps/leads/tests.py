"""
Lead Tests - Test cases for Lead model and API.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from django.contrib.auth import get_user_model

from .models import Lead

User = get_user_model()


class LeadModelTest(TestCase):
    """Test cases for Lead model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.lead_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'company': 'Test Company',
            'company_site': 'https://testcompany.com',
            'contact_type': Lead.ContactTypeChoices.EMAIL,
            'contact_value': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'extra': {'source': 'contact_form'},
            'site_url': 'https://example.com/contact',
            'user_agent': 'Mozilla/5.0 (Test Browser)',
            'ip_address': '127.0.0.1',
            'status': Lead.StatusChoices.NEW,
            'user': self.user
        }
    
    def test_create_lead(self):
        """Test creating a lead."""
        lead = Lead.objects.create(**self.lead_data)
        
        self.assertEqual(lead.name, 'John Doe')
        self.assertEqual(lead.email, 'john@example.com')
        self.assertEqual(lead.company, 'Test Company')
        self.assertEqual(lead.contact_type, Lead.ContactTypeChoices.EMAIL)
        self.assertEqual(lead.status, Lead.StatusChoices.NEW)
        self.assertEqual(lead.user, self.user)
        self.assertIsNotNone(lead.created_at)
        self.assertIsNotNone(lead.updated_at)
    
    def test_lead_str_representation(self):
        """Test string representation of lead."""
        lead = Lead.objects.create(**self.lead_data)
        expected_str = f"John Doe - https://example.com/contact (new)"
        self.assertEqual(str(lead), expected_str)
    
    def test_lead_choices(self):
        """Test lead choices."""
        # Test status choices
        status_choices = [choice[0] for choice in Lead.StatusChoices.choices]
        self.assertIn('new', status_choices)
        self.assertIn('contacted', status_choices)
        self.assertIn('qualified', status_choices)
        self.assertIn('converted', status_choices)
        self.assertIn('rejected', status_choices)
        
        # Test contact type choices
        contact_choices = [choice[0] for choice in Lead.ContactTypeChoices.choices]
        self.assertIn('email', contact_choices)
        self.assertIn('whatsapp', contact_choices)
        self.assertIn('telegram', contact_choices)
        self.assertIn('phone', contact_choices)
        self.assertIn('other', contact_choices)
    
    def test_lead_without_user(self):
        """Test creating lead without user."""
        lead_data = self.lead_data.copy()
        del lead_data['user']
        
        lead = Lead.objects.create(**lead_data)
        self.assertIsNone(lead.user)
    
    def test_lead_optional_fields(self):
        """Test creating lead with optional fields."""
        lead_data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'Test message',
            'site_url': 'https://example.com/contact',
            'status': Lead.StatusChoices.NEW
        }
        
        lead = Lead.objects.create(**lead_data)
        self.assertEqual(lead.name, 'Jane Doe')
        self.assertIsNone(lead.company)
        self.assertIsNone(lead.company_site)
        self.assertEqual(lead.contact_type, Lead.ContactTypeChoices.EMAIL)  # default
        self.assertIsNone(lead.contact_value)
        self.assertIsNone(lead.subject)
        self.assertIsNone(lead.extra)


class LeadAPITest(APITestCase):
    """Test cases for Lead API."""
    
    def setUp(self):
        """Set up test data."""
        self.url = reverse('leads:lead-submit')
        self.valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'company': 'Test Company',
            'company_site': 'https://testcompany.com',
            'contact_type': 'email',
            'contact_value': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'extra': {'source': 'contact_form'},
            'site_url': 'https://example.com/contact'
        }
    
    def test_submit_lead_success(self):
        """Test successful lead submission."""
        response = self.client.post(self.url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Lead submitted successfully')
        self.assertIn('lead_id', response.data)
        
        # Check if lead was created
        lead = Lead.objects.get(id=response.data['lead_id'])
        self.assertEqual(lead.name, 'John Doe')
        self.assertEqual(lead.email, 'john@example.com')
        self.assertEqual(lead.status, Lead.StatusChoices.NEW)
        self.assertIsNotNone(lead.ip_address)
        self.assertIsNotNone(lead.user_agent)
    
    def test_submit_lead_missing_required_fields(self):
        """Test lead submission with missing required fields."""
        # Test missing name
        data = self.valid_data.copy()
        del data['name']
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('name', response.data['details'])
        
        # Test missing email
        data = self.valid_data.copy()
        del data['email']
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['details'])
        
        # Test missing message
        data = self.valid_data.copy()
        del data['message']
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('message', response.data['details'])
    
    def test_submit_lead_invalid_email(self):
        """Test lead submission with invalid email."""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', response.data['details'])
    
    def test_submit_lead_minimal_data(self):
        """Test lead submission with minimal required data."""
        minimal_data = {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'message': 'Test message',
            'site_url': 'https://example.com/contact'
        }
        
        response = self.client.post(self.url, minimal_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Check if lead was created with defaults
        lead = Lead.objects.get(id=response.data['lead_id'])
        self.assertEqual(lead.name, 'Jane Doe')
        self.assertEqual(lead.email, 'jane@example.com')
        self.assertEqual(lead.contact_type, Lead.ContactTypeChoices.EMAIL)  # default
        self.assertIsNone(lead.company)
        self.assertIsNone(lead.company_site)
        self.assertIsNone(lead.subject)
        self.assertIsNone(lead.extra)
    
    def test_submit_lead_different_contact_types(self):
        """Test lead submission with different contact types."""
        contact_types = ['email', 'whatsapp', 'telegram', 'phone', 'other']
        
        for contact_type in contact_types:
            data = self.valid_data.copy()
            data['contact_type'] = contact_type
            data['contact_value'] = f'test_{contact_type}@example.com'
            
            response = self.client.post(self.url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(response.data['success'])
            
            lead = Lead.objects.get(id=response.data['lead_id'])
            self.assertEqual(lead.contact_type, contact_type)
    
    def test_submit_lead_with_extra_data(self):
        """Test lead submission with extra JSON data."""
        data = self.valid_data.copy()
        data['extra'] = {
            'source': 'contact_form',
            'utm_source': 'google',
            'utm_medium': 'cpc',
            'utm_campaign': 'test_campaign',
            'user_agent_info': {
                'browser': 'Chrome',
                'version': '91.0'
            }
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        lead = Lead.objects.get(id=response.data['lead_id'])
        self.assertEqual(lead.extra, data['extra'])
    
    def test_submit_lead_ip_and_user_agent(self):
        """Test that IP address and user agent are captured."""
        # Set custom headers
        headers = {
            'HTTP_X_FORWARDED_FOR': '192.168.1.100',
            'HTTP_USER_AGENT': 'Test Browser/1.0'
        }
        
        response = self.client.post(self.url, self.valid_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        lead = Lead.objects.get(id=response.data['lead_id'])
        self.assertEqual(lead.ip_address, '192.168.1.100')
        self.assertEqual(lead.user_agent, 'Test Browser/1.0')
    
    def test_submit_lead_without_forwarded_ip(self):
        """Test IP capture when X-Forwarded-For is not present."""
        response = self.client.post(self.url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        lead = Lead.objects.get(id=response.data['lead_id'])
        # Should capture some IP (could be 127.0.0.1 in tests)
        self.assertIsNotNone(lead.ip_address)
