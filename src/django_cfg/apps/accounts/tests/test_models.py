from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from ..models import OTPSecret, RegistrationSource, UserRegistrationSource

User = get_user_model()


class CustomUserModelTest(TestCase):
    """Test CustomUser model."""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(**self.user_data)

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_admin)

    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')

    def test_email_unique(self):
        """Test email uniqueness."""
        User.objects.create_user(**self.user_data)

        with self.assertRaises(Exception):
            User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test user creation."""
        user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        user = User.objects.create_user(**user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class OTPSecretModelTest(TestCase):
    """Test OTPSecret model."""

    def setUp(self):
        self.email = 'test@example.com'

    def test_otp_generation(self):
        """Test OTP generation."""
        otp = OTPSecret.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_otp_creation(self):
        """Test OTP creation."""
        otp = OTPSecret.objects.create(
            email=self.email,
            secret='123456'
        )
        self.assertEqual(otp.email, self.email)
        self.assertEqual(otp.secret, '123456')
        self.assertFalse(otp.is_used)
        self.assertIsNotNone(otp.expires_at)

    def test_otp_expiration(self):
        """Test OTP expiration."""
        # Create OTP with past expiration
        past_time = timezone.now() - timedelta(minutes=1)
        otp = OTPSecret.objects.create(
            email=self.email,
            secret='123456',
            expires_at=past_time
        )
        self.assertFalse(otp.is_valid)

    def test_otp_mark_used(self):
        """Test marking OTP as used."""
        otp = OTPSecret.objects.create(
            email=self.email,
            secret='123456'
        )
        self.assertFalse(otp.is_used)
        otp.mark_used()
        self.assertTrue(otp.is_used)

    def test_otp_str_representation(self):
        """Test OTP string representation."""
        otp = OTPSecret.objects.create(
            email=self.email,
            secret='123456'
        )
        self.assertEqual(str(otp), f"OTP for {self.email}")


class RegistrationSourceModelTest(TestCase):
    """Test RegistrationSource model."""

    def setUp(self):
        self.source = RegistrationSource.objects.create(
            url='https://dashboard.unrealon.com',
            name='Unreal Dashboard',
            description='Main dashboard for Unreal project',
            is_active=True
        )

    def test_source_creation(self):
        """Test source creation."""
        self.assertEqual(self.source.url, 'https://dashboard.unrealon.com')
        self.assertEqual(self.source.name, 'Unreal Dashboard')
        self.assertEqual(self.source.description, 'Main dashboard for Unreal project')
        self.assertTrue(self.source.is_active)
        self.assertIsNotNone(self.source.created_at)
        self.assertIsNotNone(self.source.updated_at)

    def test_source_get_domain(self):
        """Test domain extraction from URL."""
        test_cases = [
            ('https://test1.unrealon.com', 'test1.unrealon.com'),
            ('https://www.example.com', 'www.example.com'),
            ('http://app.test.com', 'app.test.com'),
            ('https://sub.domain.co.uk', 'sub.domain.co.uk'),
        ]
        
        for url, expected_domain in test_cases:
            source = RegistrationSource.objects.create(url=url)
            self.assertEqual(source.get_domain(), expected_domain)

    def test_source_get_display_name(self):
        """Test display name generation."""
        # Source with custom name
        source_with_name = RegistrationSource.objects.create(
            url='https://example.com',
            name='Custom Name'
        )
        self.assertEqual(source_with_name.get_display_name(), 'Custom Name')
        
        # Source without name (uses domain)
        source_without_name = RegistrationSource.objects.create(
            url='https://app.example.com'
        )
        self.assertEqual(source_without_name.get_display_name(), 'app.example.com')

    def test_source_str_representation(self):
        """Test source string representation."""
        # Source with custom name
        source_with_name = RegistrationSource.objects.create(
            url='https://example.com',
            name='Custom Name'
        )
        self.assertEqual(str(source_with_name), 'Custom Name')
        
        # Source without name (uses domain)
        source_without_name = RegistrationSource.objects.create(
            url='https://app.example.com'
        )
        self.assertEqual(str(source_without_name), 'app.example.com')

    def test_source_unique_url(self):
        """Test that source URL must be unique."""
        RegistrationSource.objects.create(url='https://example.com')
        
        # Try to create another source with same URL
        with self.assertRaises(Exception):  # Should raise IntegrityError
            RegistrationSource.objects.create(url='https://example.com')

    def test_source_ordering(self):
        """Test source ordering by created_at descending."""
        source1 = RegistrationSource.objects.create(url='https://example1.com')
        source2 = RegistrationSource.objects.create(url='https://example2.com')
        
        sources = RegistrationSource.objects.all()
        self.assertEqual(sources[0], source2)  # Most recent first
        self.assertEqual(sources[1], source1)


class UserRegistrationSourceModelTest(TestCase):
    """Test UserRegistrationSource model."""

    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            username='testuser'
        )
        self.source = RegistrationSource.objects.create(
            url='https://dashboard.unrealon.com',
            name='Unreal Dashboard'
        )

    def test_user_source_creation(self):
        """Test user-source relationship creation."""
        user_source = UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source,
            first_registration=True
        )
        
        self.assertEqual(user_source.user, self.user)
        self.assertEqual(user_source.source, self.source)
        self.assertTrue(user_source.first_registration)
        self.assertIsNotNone(user_source.registration_date)

    def test_user_source_unique_constraint(self):
        """Test that user-source relationship is unique."""
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source,
            first_registration=True
        )
        
        # Try to create duplicate relationship
        with self.assertRaises(Exception):  # Should raise IntegrityError
            UserRegistrationSource.objects.create(
                user=self.user,
                source=self.source,
                first_registration=False
            )

    def test_user_source_ordering(self):
        """Test user-source ordering by registration_date descending."""
        user_source1 = UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source,
            first_registration=True
        )
        
        # Create another source and relationship
        source2 = RegistrationSource.objects.create(url='https://example.com')
        user_source2 = UserRegistrationSource.objects.create(
            user=self.user,
            source=source2,
            first_registration=False
        )
        
        user_sources = UserRegistrationSource.objects.all()
        self.assertEqual(user_sources[0], user_source2)  # Most recent first
        self.assertEqual(user_sources[1], user_source1)


class CustomUserSourceMethodsTest(TestCase):
    """Test CustomUser source-related methods."""

    def setUp(self):
        self.user = User.objects.create(
            email='test@example.com',
            username='testuser'
        )
        self.source1 = RegistrationSource.objects.create(
            url='https://dashboard.unrealon.com',
            name='Unreal Dashboard'
        )
        self.source2 = RegistrationSource.objects.create(
            url='https://app.example.com',
            name='Example App'
        )

    def test_user_get_sources(self):
        """Test user get_sources method."""
        # Create user-source relationships
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source1,
            first_registration=True
        )
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source2,
            first_registration=False
        )
        
        sources = self.user.get_sources()
        self.assertEqual(sources.count(), 2)
        self.assertIn(self.source1, sources)
        self.assertIn(self.source2, sources)

    def test_user_get_primary_source(self):
        """Test user get_primary_source method."""
        # Create user-source relationships
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source1,
            first_registration=True
        )
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source2,
            first_registration=False
        )
        
        primary_source = self.user.get_primary_source()
        self.assertEqual(primary_source, self.source1)

    def test_user_no_sources(self):
        """Test user methods when no sources exist."""
        sources = self.user.get_sources()
        self.assertEqual(sources.count(), 0)
        
        primary_source = self.user.get_primary_source()
        self.assertIsNone(primary_source)

    def test_user_multiple_first_registrations(self):
        """Test behavior when multiple sources have first_registration=True."""
        # Create multiple sources with first_registration=True
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source1,
            first_registration=True
        )
        UserRegistrationSource.objects.create(
            user=self.user,
            source=self.source2,
            first_registration=True
        )
        
        # Should return the first one (by registration_date)
        primary_source = self.user.get_primary_source()
        self.assertIsNotNone(primary_source)
        self.assertIn(primary_source, [self.source1, self.source2])
