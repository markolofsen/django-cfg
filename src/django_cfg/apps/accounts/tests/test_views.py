from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from ..models import OTPSecret

User = get_user_model()


class OTPViewsTest(APITestCase):
    """Test OTP authentication views."""
    
    def setUp(self):
        self.email = "test@example.com"
        self.source_url = "https://dashboard.unrealon.com"
        self.otp_request_url = reverse("otp-request-otp")
        self.otp_verify_url = reverse("otp-verify-otp")

    @patch("apps.accounts.services.otp_service.OTPService.request_otp")
    def test_otp_request_success(self, mock_request_otp):
        """Test successful OTP request."""
        mock_request_otp.return_value = (True, "success")

        data = {"email": self.email}
        response = self.client.post(self.otp_request_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_request_otp.assert_called_once_with(self.email, None)

    @patch("apps.accounts.services.otp_service.OTPService.request_otp")
    def test_otp_request_with_source_url(self, mock_request_otp):
        """Test successful OTP request with source_url."""
        mock_request_otp.return_value = (True, "success")

        data = {"email": self.email, "source_url": self.source_url}
        response = self.client.post(self.otp_request_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        mock_request_otp.assert_called_once_with(self.email, self.source_url)

    @patch("apps.accounts.services.otp_service.OTPService.request_otp")
    def test_otp_request_failure(self, mock_request_otp):
        """Test OTP request failure."""
        mock_request_otp.return_value = (False, "email_send_failed")

        data = {"email": self.email}
        response = self.client.post(self.otp_request_url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    def test_otp_request_invalid_email(self):
        """Test OTP request with invalid email."""
        data = {"email": "invalid-email"}
        response = self.client.post(self.otp_request_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_request_missing_email(self):
        """Test OTP request without email."""
        response = self.client.post(self.otp_request_url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_request_invalid_source_url(self):
        """Test OTP request with invalid source_url."""
        data = {"email": self.email, "source_url": "not-a-url"}
        response = self.client.post(self.otp_request_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.accounts.services.otp_service.OTPService.verify_otp")
    def test_otp_verify_success(self, mock_verify_otp):
        """Test successful OTP verification."""
        user = User.objects.create_user(email=self.email, username="testuser")
        mock_verify_otp.return_value = user

        data = {"email": self.email, "otp": "123456"}
        response = self.client.post(self.otp_verify_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.email)

    @patch("apps.accounts.services.otp_service.OTPService.verify_otp")
    def test_otp_verify_with_source_url(self, mock_verify_otp):
        """Test successful OTP verification with source_url."""
        user = User.objects.create_user(email=self.email, username="testuser")
        mock_verify_otp.return_value = user

        data = {"email": self.email, "otp": "123456", "source_url": self.source_url}
        response = self.client.post(self.otp_verify_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        mock_verify_otp.assert_called_once_with(self.email, "123456", self.source_url)

    @patch("apps.accounts.services.otp_service.OTPService.verify_otp")
    def test_otp_verify_failure(self, mock_verify_otp):
        """Test OTP verification failure."""
        mock_verify_otp.return_value = None

        data = {"email": self.email, "otp": "123456"}
        response = self.client.post(self.otp_verify_url, data)

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertIn("error", response.data)

    def test_otp_verify_invalid_data(self):
        """Test OTP verification with invalid data."""
        # Invalid OTP length
        data = {"email": self.email, "otp": "12345"}  # Too short
        response = self.client.post(self.otp_verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid OTP characters
        data = {"email": self.email, "otp": "12345a"}  # Contains letter
        response = self.client.post(self.otp_verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Missing required fields
        data = {"source_url": self.source_url}
        response = self.client.post(self.otp_verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserViewsTest(APITestCase):
    """Test user profile views."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def test_user_detail_authenticated(self):
        """Test getting user detail when authenticated."""
        url = reverse("profile_detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        # username field removed from serializer

    def test_user_detail_unauthenticated(self):
        """Test getting user detail when not authenticated."""
        self.client.force_authenticate(user=None)
        url = reverse("profile_detail")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshViewTest(APITestCase):
    """Test token refresh view."""
    
    

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser"
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        url = reverse("token_refresh")
        data = {"refresh": str(self.refresh)}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        url = reverse("token_refresh")
        data = {"refresh": "invalid-token"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_missing_token(self):
        """Test token refresh without token."""
        url = reverse("token_refresh")
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IntegrationTest(APITestCase):
    """Integration tests for OTP flow."""
    
    

    def setUp(self):
        self.email = "test@example.com"
        self.otp_request_url = reverse("otp-request-otp")
        self.otp_verify_url = reverse("otp-verify-otp")

    @patch("apps.mailer.services.email_service.EmailService.send_templated_email")
    def test_full_otp_flow(self, mock_email):
        """Test complete OTP flow."""
        mock_email.return_value = True

        # Step 1: Request OTP
        data = {"email": self.email}
        response = self.client.post(self.otp_request_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Step 2: Get OTP from database
        otp = OTPSecret.objects.get(email=self.email)
        self.assertIsNotNone(otp)

        # Step 3: Verify OTP
        data = {"email": self.email, "otp": otp.secret}
        response = self.client.post(self.otp_verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    @patch("apps.mailer.services.email_service.EmailService.send_templated_email")
    def test_full_otp_flow_with_source_url(self, mock_email):
        """Test complete OTP flow with source_url."""
        mock_email.return_value = True

        # Step 1: Request OTP with source_url
        data = {"email": self.email, "source_url": "https://dashboard.unrealon.com"}
        response = self.client.post(self.otp_request_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Step 2: Get OTP from database
        otp = OTPSecret.objects.get(email=self.email)
        self.assertIsNotNone(otp)

        # Step 3: Verify OTP with source_url
        data = {
            "email": self.email,
            "otp": otp.secret,
            "source_url": "https://dashboard.unrealon.com",
        }
        response = self.client.post(self.otp_verify_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
