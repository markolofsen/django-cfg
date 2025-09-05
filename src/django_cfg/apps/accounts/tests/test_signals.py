"""
Tests for account signals and email notifications.
"""

import logging
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import call_command

from django_cfg.apps.accounts.signals import trigger_login_notification
from django_cfg.apps.accounts.utils.auth_email_service import AuthEmailService
from django_cfg.apps.billing.models import Tariff, Subscription

User = get_user_model()


class AccountSignalsTestCase(TestCase):
    """Test cases for account signals."""

    def setUp(self):
        """Set up test data."""
        call_command("create_default_tariffs")
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_welcome_email")
    def test_user_registration_signal(self, mock_send_welcome):
        """Test that welcome email is sent when new user is created."""
        # Create new user
        user = User.objects.create(**self.user_data)

        # Check that welcome email was sent
        mock_send_welcome.assert_called_once_with(user.username)

    def test_user_profile_update_signal(self):
        """Test that security alert is sent when user profile is updated."""
        with patch(
            "apps.accounts.utils.auth_email_service.AuthEmailService.send_security_alert_email"
        ) as mock_send_security:
            user = User.objects.create(**self.user_data)

            # Assign free plan subscription
            free_tariff = Tariff.objects.get(slug="free")
            subscription = Subscription.objects.create(user=user, tariff=free_tariff)

            # Change email directly on the user object and save
            user.email = "newemail@example.com"
            user.save()

            # Check that the signal was triggered
            mock_send_security.assert_called()
            args, kwargs = mock_send_security.call_args
            assert "email address" in args[1]

    def test_signal_error_handling(self):
        """Test that signals handle errors gracefully."""
        with patch(
            "apps.accounts.utils.auth_email_service.AuthEmailService.send_welcome_email",
            side_effect=Exception("Email service error"),
        ):
            user = User.objects.create(**self.user_data)
            # Test passes if no exception is raised

    def test_multiple_profile_changes(self):
        """Test that security alert is sent for multiple profile changes."""
        with patch(
            "apps.accounts.utils.auth_email_service.AuthEmailService.send_security_alert_email"
        ) as mock_send:
            user = User.objects.create(**self.user_data)

            # Assign free plan subscription
            free_tariff = Tariff.objects.get(slug="free")
            subscription = Subscription.objects.create(user=user, tariff=free_tariff)

            # Change multiple fields directly on the user object
            user.email = "newemail@example.com"
            user.username = "newusername"
            user.first_name = "New"
            user.save()

            mock_send.assert_called()
            args, kwargs = mock_send.call_args
            assert "email address" in args[1]
            assert "username" in args[1]
            assert "name" in args[1]


