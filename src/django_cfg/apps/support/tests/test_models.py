from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from unittest.mock import patch
from ..models import Ticket, Message

User = get_user_model()

class TicketModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser', email='user@example.com')

    def test_create_ticket_default_status(self):
        ticket = Ticket.objects.create(user=self.user, subject='Test subject')
        self.assertEqual(Ticket.TicketStatus, Ticket.TicketStatus.OPEN)
        self.assertEqual(str(ticket), f"Ticket #{ticket.pk} - {self.user.username} (Open)")
        self.assertTrue(ticket.uuid)

    def test_ticket_status_choices(self):
        ticket = Ticket.objects.create(user=self.user, subject='Test', status=Ticket.TicketStatus.RESOLVED)
        self.assertEqual(Ticket.TicketStatus, Ticket.TicketStatus.RESOLVED)
        self.assertEqual(ticket.get_status_display(), 'Resolved')

    def test_ticket_ordering(self):
        """Test that tickets are ordered by created_at descending."""
        ticket1 = Ticket.objects.create(user=self.user, subject='First ticket')
        ticket2 = Ticket.objects.create(user=self.user, subject='Second ticket')
        
        # Get tickets in default ordering
        tickets = list(Ticket.objects.all())
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(tickets[0], ticket2)
        self.assertEqual(tickets[1], ticket1)


class UserModelTest(TestCase):
    def test_display_username_with_username(self):
        """Test display_username property with username."""
        user = User.objects.create(
            username='test_user_123',
            email='test@example.com'
        )
        self.assertEqual(user.display_username, 'Test User 123')

    def test_display_username_with_special_chars(self):
        """Test display_username property with special characters."""
        user = User.objects.create(
            username='test-user.123',
            email='test@example.com'
        )
        self.assertEqual(user.display_username, 'Test User 123')

    def test_display_username_fallback_to_name(self):
        """Test display_username property falls back to full name."""
        user = User.objects.create(
            username='',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.display_username, 'John Doe')

    def test_display_username_fallback_to_email(self):
        """Test display_username property falls back to email."""
        user = User.objects.create(
            username='',
            email='john.doe@example.com'
        )
        self.assertEqual(user.display_username, 'John.doe')


class MessageModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='testuser', email='user@example.com')
        self.admin = get_user_model().objects.create(username='admin', is_staff=True, email='admin@example.com')
        self.ticket = Ticket.objects.create(user=self.user, subject='Test subject')

    def test_create_message_user(self):
        msg = Message.objects.create(ticket=self.ticket, sender=self.user, text='Hello')
        self.assertEqual(msg.ticket, self.ticket)
        self.assertEqual(msg.sender, self.user)
        self.assertFalse(msg.sender.is_staff)
        self.assertEqual(msg.text, 'Hello')
        self.assertTrue(msg.uuid)

    def test_create_message_admin(self):
        msg = Message.objects.create(ticket=self.ticket, sender=self.admin, text='Admin reply')
        self.assertEqual(msg.ticket, self.ticket)
        self.assertEqual(msg.sender, self.admin)
        self.assertTrue(msg.sender.is_staff)
        self.assertEqual(msg.text, 'Admin reply')
        self.assertTrue(msg.uuid)

    def test_message_ordering(self):
        Message.objects.create(ticket=self.ticket, sender=self.user, text='First')
        Message.objects.create(ticket=self.ticket, sender=self.user, text='Second')
        messages = list(self.ticket.messages.all())
        self.assertEqual(messages[0].text, 'First')
        self.assertEqual(messages[1].text, 'Second')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @patch('django.core.mail.EmailMultiAlternatives.send')
    def test_send_support_reply_email(self, mock_send):
        msg = Message.objects.create(ticket=self.ticket, sender=self.admin, text='Admin reply')
        Message.objects.send_support_reply_email(msg)
        self.assertTrue(mock_send.called) 