from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch
from datetime import timedelta

from ..services import OTPService
from ..models import OTPSecret, RegistrationSource, UserRegistrationSource

User = get_user_model()


class OTPServiceTest(TestCase):
    """Test OTPService."""

    def setUp(self):
        self.email = "test@example.com"
        self.source_url = "https://dashboard.unrealon.com"

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_otp_email")
    def test_request_otp_new_user(self, mock_email):
        """Test OTP request for new user."""
        mock_email.return_value = True

        success, error_type = OTPService.request_otp(self.email)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # User should be created
        user = User.objects.get(email=self.email)
        self.assertIsNotNone(user)

        # OTP should be created
        otp = OTPSecret.objects.get(email=self.email)
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp.secret), 6)
        self.assertTrue(otp.secret.isdigit())

        # Email should be sent
        mock_email.assert_called_once()

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_otp_email")
    def test_request_otp_new_user_with_source_url(self, mock_email):
        """Test OTP request for new user with source_url."""
        mock_email.return_value = True

        success, error_type = OTPService.request_otp(self.email, self.source_url)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # User should be created
        user = User.objects.get(email=self.email)
        self.assertIsNotNone(user)

        # Source should be created
        source = RegistrationSource.objects.get(url=self.source_url)
        self.assertIsNotNone(source)
        self.assertEqual(source.name, "dashboard.unrealon.com")

        # User-source relationship should be created
        user_source = UserRegistrationSource.objects.get(user=user, source=source)
        self.assertIsNotNone(user_source)
        self.assertTrue(user_source.first_registration)

        # OTP should be created
        otp = OTPSecret.objects.get(email=self.email)
        self.assertIsNotNone(otp)

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_otp_email")
    def test_request_otp_existing_user(self, mock_email):
        """Test OTP request for existing user."""
        mock_email.return_value = True

        # Create existing user
        User.objects.create_user(email=self.email, username="existing_user")

        success, error_type = OTPService.request_otp(self.email)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Should not create duplicate user
        users = User.objects.filter(email=self.email)
        self.assertEqual(users.count(), 1)

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_otp_email")
    def test_request_otp_existing_user_with_source_url(self, mock_email):
        """Test OTP request for existing user with source_url."""
        mock_email.return_value = True

        # Create existing user
        user = User.objects.create_user(email=self.email, username="existing_user")

        success, error_type = OTPService.request_otp(self.email, self.source_url)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Source should be created
        source = RegistrationSource.objects.get(url=self.source_url)
        self.assertIsNotNone(source)

        # User-source relationship should be created
        user_source = UserRegistrationSource.objects.get(user=user, source=source)
        self.assertIsNotNone(user_source)
        self.assertFalse(user_source.first_registration)  # Not first registration

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_otp_email")
    def test_request_otp_reuse_active(self, mock_email):
        """Test OTP request reuses active OTP."""
        mock_email.return_value = True

        # Create existing OTP
        OTPSecret.objects.create(email=self.email, secret="123456")

        success, error_type = OTPService.request_otp(self.email)

        self.assertTrue(success)
        self.assertEqual(error_type, "success")

        # Should reuse existing OTP
        otp_count = OTPSecret.objects.filter(email=self.email).count()
        self.assertEqual(otp_count, 1)

        # Should use existing secret
        otp = OTPSecret.objects.get(email=self.email)
        self.assertEqual(otp.secret, "123456")

    @patch("apps.accounts.utils.auth_email_service.AuthEmailService.send_otp_email")
    def test_request_otp_email_failure(self, mock_email):
        """Test OTP request when email fails."""
        mock_email.side_effect = Exception("Email service error")

        success, error_type = OTPService.request_otp(self.email)

        self.assertFalse(success)
        self.assertEqual(error_type, "email_send_failed")

    def test_request_otp_invalid_email(self):
        """Test OTP request with invalid email."""
        success, error_type = OTPService.request_otp("")

        self.assertFalse(success)
        self.assertEqual(error_type, "invalid_email")

    def test_verify_otp_success(self):
        """Test successful OTP verification."""
        # Create user and OTP
        user = User.objects.create_user(email=self.email, username="testuser")
        otp = OTPSecret.objects.create(email=self.email, secret="123456")

        # Verify OTP
        result_user = OTPService.verify_otp(self.email, "123456")

        self.assertIsNotNone(result_user)
        self.assertEqual(result_user, user)

        # OTP should be marked as used
        otp.refresh_from_db()
        self.assertTrue(otp.is_used)

    def test_verify_otp_success_with_source_url(self):
        """Test successful OTP verification with source_url."""
        # Create user and OTP
        user = User.objects.create_user(email=self.email, username="testuser")
        otp = OTPSecret.objects.create(email=self.email, secret="123456")

        # Verify OTP with source_url
        result_user = OTPService.verify_otp(self.email, "123456", self.source_url)

        self.assertIsNotNone(result_user)
        self.assertEqual(result_user, user)

        # Source should be created
        source = RegistrationSource.objects.get(url=self.source_url)
        self.assertIsNotNone(source)

        # User-source relationship should be created
        user_source = UserRegistrationSource.objects.get(user=user, source=source)
        self.assertIsNotNone(user_source)
        self.assertFalse(user_source.first_registration)  # Not first registration

    def test_verify_otp_invalid_code(self):
        """Test OTP verification with invalid code."""
        # Create user and OTP
        User.objects.create_user(email=self.email, username="testuser")
        OTPSecret.objects.create(email=self.email, secret="123456")

        # Try to verify with wrong code
        result_user = OTPService.verify_otp(self.email, "654321")

        self.assertIsNone(result_user)

    def test_verify_otp_expired(self):
        """Test OTP verification with expired OTP."""
        # Create user and expired OTP
        User.objects.create_user(email=self.email, username="testuser")
        expired_time = timezone.now() - timedelta(minutes=11)
        OTPSecret.objects.create(
            email=self.email, secret="123456", expires_at=expired_time
        )

        # Try to verify expired OTP
        result_user = OTPService.verify_otp(self.email, "123456")

        self.assertIsNone(result_user)

    def test_verify_otp_used(self):
        """Test OTP verification with used OTP."""
        # Create user and used OTP
        User.objects.create_user(email=self.email, username="testuser")
        OTPSecret.objects.create(email=self.email, secret="123456", is_used=True)

        # Try to verify used OTP
        result_user = OTPService.verify_otp(self.email, "123456")

        self.assertIsNone(result_user)

    def test_verify_otp_no_user(self):
        """Test OTP verification when user doesn't exist."""
        # Create OTP but no user
        OTPSecret.objects.create(email=self.email, secret="123456")

        # Try to verify OTP
        result_user = OTPService.verify_otp(self.email, "123456")

        self.assertIsNone(result_user)

    def test_verify_otp_invalid_input(self):
        """Test OTP verification with invalid input."""
        # Test with empty email
        result_user = OTPService.verify_otp("", "123456")
        self.assertIsNone(result_user)

        # Test with empty OTP
        result_user = OTPService.verify_otp(self.email, "")
        self.assertIsNone(result_user)

        # Test with None values
        result_user = OTPService.verify_otp(None, "123456")
        self.assertIsNone(result_user)

        result_user = OTPService.verify_otp(self.email, None)
        self.assertIsNone(result_user)
