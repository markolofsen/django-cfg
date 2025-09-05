import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django_cfg.apps.accounts.serializers.profile import (
    UserProfileUpdateSerializer,
    RegistrationSourceSerializer,
    UserRegistrationSourceSerializer,
    UserWithSourcesSerializer,
)
from django_cfg.apps.accounts.serializers.otp import OTPRequestSerializer, OTPVerifySerializer
from django_cfg.apps.accounts.models import RegistrationSource, UserRegistrationSource

User = get_user_model()

# Disable Telegram notifications in tests
os.environ["TELEGRAM_DISABLED"] = "true"


class UserProfileUpdateSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )

    def test_valid_first_name_update(self):
        """Test valid first name update."""
        data = {"first_name": "Jane"}
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["first_name"], "Jane")

    def test_first_name_too_short(self):
        """Test first name validation - too short."""
        data = {"first_name": "J"}
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_valid_last_name_update(self):
        """Test valid last name update."""
        data = {"last_name": "Smith"}
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["last_name"], "Smith")

    def test_last_name_too_short(self):
        """Test last name validation - too short."""
        data = {"last_name": "S"}
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("last_name", serializer.errors)

    def test_valid_phone_update(self):
        """Test valid phone update."""
        data = {"phone": "+1 (555) 123-4567"}
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["phone"], "+1 (555) 123-4567")

    def test_invalid_phone(self):
        """Test phone validation - invalid format."""
        data = {"phone": "invalid-phone"}
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("phone", serializer.errors)

    def test_multiple_fields_update(self):
        """Test updating multiple fields at once."""
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "Tech Corp",
            "position": "Developer",
        }
        serializer = UserProfileUpdateSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["first_name"], "Jane")
        self.assertEqual(serializer.validated_data["last_name"], "Smith")
        self.assertEqual(serializer.validated_data["company"], "Tech Corp")
        self.assertEqual(serializer.validated_data["position"], "Developer")


class RegistrationSourceSerializerTest(TestCase):
    def setUp(self):
        self.source = RegistrationSource.objects.create(
            url="https://dashboard.unrealon.com",
            name="Unreal Dashboard",
            description="Main dashboard for Unreal project",
            is_active=True,
        )

    def test_source_serializer_fields(self):
        """Test RegistrationSource serializer includes all required fields."""
        serializer = RegistrationSourceSerializer(self.source)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("url", data)
        self.assertIn("name", data)
        self.assertIn("description", data)
        self.assertIn("is_active", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

        self.assertEqual(data["url"], "https://dashboard.unrealon.com")
        self.assertEqual(data["name"], "Unreal Dashboard")
        self.assertEqual(data["description"], "Main dashboard for Unreal project")
        self.assertTrue(data["is_active"])

    def test_source_serializer_validation(self):
        """Test RegistrationSource serializer validation."""
        data = {
            "url": "https://test.example.com",
            "name": "Test Source",
            "description": "Test description",
            "is_active": True,
        }
        serializer = RegistrationSourceSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class UserRegistrationSourceSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", email="test@example.com")
        self.source = RegistrationSource.objects.create(
            url="https://dashboard.unrealon.com", name="Unreal Dashboard"
        )
        self.user_source = UserRegistrationSource.objects.create(
            user=self.user, source=self.source, first_registration=True
        )

    def test_user_source_serializer_fields(self):
        """Test UserRegistrationSource serializer includes all required fields."""
        serializer = UserRegistrationSourceSerializer(self.user_source)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("user", data)
        self.assertIn("source", data)
        self.assertIn("first_registration", data)
        self.assertIn("registration_date", data)

        self.assertEqual(data["user"], self.user.id)
        self.assertTrue(data["first_registration"])

        # Check nested source data
        source_data = data["source"]
        self.assertEqual(source_data["url"], "https://dashboard.unrealon.com")
        self.assertEqual(source_data["name"], "Unreal Dashboard")

    def test_user_source_serializer_validation(self):
        """Test UserRegistrationSource serializer validation."""
        data = {
            "user": self.user.id,
            "source": self.source.id,
            "first_registration": False,
        }
        serializer = UserRegistrationSourceSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class UserWithSourcesSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
        )
        self.source1 = RegistrationSource.objects.create(
            url="https://dashboard.unrealon.com", name="Unreal Dashboard"
        )
        self.source2 = RegistrationSource.objects.create(
            url="https://app.example.com", name="Example App"
        )
        self.user_source1 = UserRegistrationSource.objects.create(
            user=self.user, source=self.source1, first_registration=True
        )
        self.user_source2 = UserRegistrationSource.objects.create(
            user=self.user, source=self.source2, first_registration=False
        )

    def test_user_with_sources_serializer_fields(self):
        """Test UserWithSources serializer includes sources information."""
        serializer = UserWithSourcesSerializer(self.user)
        data = serializer.data

        # Check basic user fields
        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertIn("first_name", data)
        self.assertIn("last_name", data)

        # Check sources fields
        self.assertIn("sources", data)
        self.assertIn("primary_source", data)

        # Check sources data
        sources = data["sources"]
        self.assertEqual(len(sources), 2)

        # Check primary source
        primary_source = data["primary_source"]
        self.assertIsNotNone(primary_source)
        self.assertEqual(primary_source["url"], "https://dashboard.unrealon.com")
        self.assertEqual(primary_source["name"], "Unreal Dashboard")

    def test_user_with_sources_no_sources(self):
        """Test UserWithSources serializer for user without sources."""
        user_without_sources = User.objects.create(
            username="nosources", email="nosources@example.com"
        )
        serializer = UserWithSourcesSerializer(user_without_sources)
        data = serializer.data

        self.assertEqual(len(data["sources"]), 0)
        self.assertIsNone(data["primary_source"])


class OTPRequestSerializerTest(TestCase):
    def test_valid_otp_request(self):
        """Test valid OTP request with source_url."""
        data = {
            "email": "test@example.com",
            "source_url": "https://dashboard.unrealon.com",
        }
        serializer = OTPRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertEqual(
            serializer.validated_data["source_url"], "https://dashboard.unrealon.com"
        )

    def test_valid_otp_request_without_source_url(self):
        """Test valid OTP request without source_url."""
        data = {"email": "test@example.com"}
        serializer = OTPRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertNotIn("source_url", serializer.validated_data)

    def test_valid_otp_request_empty_source_url(self):
        """Test valid OTP request with empty source_url."""
        data = {"email": "test@example.com", "source_url": ""}
        serializer = OTPRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertIsNone(serializer.validated_data.get("source_url"))

    def test_invalid_email(self):
        """Test invalid email in OTP request."""
        data = {
            "email": "invalid-email",
            "source_url": "https://dashboard.unrealon.com",
        }
        serializer = OTPRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_missing_email(self):
        """Test missing email in OTP request."""
        data = {"source_url": "https://dashboard.unrealon.com"}
        serializer = OTPRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_invalid_source_url(self):
        """Test invalid source_url in OTP request."""
        data = {"email": "test@example.com", "source_url": "not-a-url"}
        serializer = OTPRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("source_url", serializer.errors)


class OTPVerifySerializerTest(TestCase):
    def test_valid_otp_verify(self):
        """Test valid OTP verification with source_url."""
        data = {
            "email": "test@example.com",
            "otp": "123456",
            "source_url": "https://dashboard.unrealon.com",
        }
        serializer = OTPVerifySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertEqual(serializer.validated_data["otp"], "123456")
        self.assertEqual(
            serializer.validated_data["source_url"], "https://dashboard.unrealon.com"
        )

    def test_valid_otp_verify_without_source_url(self):
        """Test valid OTP verification without source_url."""
        data = {"email": "test@example.com", "otp": "123456"}
        serializer = OTPVerifySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "test@example.com")
        self.assertEqual(serializer.validated_data["otp"], "123456")
        self.assertNotIn("source_url", serializer.validated_data)

    def test_invalid_otp_format(self):
        """Test invalid OTP format."""
        data = {
            "email": "test@example.com",
            "otp": "12345",  # Too short
            "source_url": "https://dashboard.unrealon.com",
        }
        serializer = OTPVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("otp", serializer.errors)

    def test_invalid_otp_characters(self):
        """Test invalid OTP characters."""
        data = {
            "email": "test@example.com",
            "otp": "12345a",  # Contains letter
            "source_url": "https://dashboard.unrealon.com",
        }
        serializer = OTPVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("otp", serializer.errors)

    def test_missing_required_fields(self):
        """Test missing required fields."""
        data = {"source_url": "https://dashboard.unrealon.com"}
        serializer = OTPVerifySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertIn("otp", serializer.errors)
