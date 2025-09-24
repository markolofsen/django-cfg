from typing import Optional, List
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string
from urllib.parse import urlparse

from .managers.user_manager import UserManager


def user_avatar_path(instance, filename):
    """Generate file path for user avatar."""
    return f"avatars/{instance.id}/{filename}"


class RegistrationSource(models.Model):
    """Model for tracking user registration sources/projects."""
    url = models.URLField(unique=True, help_text="Source URL (e.g., https://unrealon.com)")
    name = models.CharField(max_length=100, blank=True, help_text="Display name for the source")
    description = models.TextField(blank=True, help_text="Optional description")
    is_active = models.BooleanField(default=True, help_text="Whether this source is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.get_domain()

    def get_domain(self):
        """Extract domain from URL."""
        try:
            parsed = urlparse(self.url)
            return parsed.netloc
        except:
            return self.url

    def get_display_name(self):
        """Get display name or domain."""
        return self.name or self.get_domain()

    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = "Registration Source"
        verbose_name_plural = "Registration Sources"
        ordering = ['-created_at']


class UserRegistrationSource(models.Model):
    """Many-to-many relationship between users and registration sources."""
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='user_registration_sources')
    source = models.ForeignKey(RegistrationSource, on_delete=models.CASCADE, related_name='user_registration_sources')
    first_registration = models.BooleanField(default=True, help_text="Whether this was the first registration from this source")
    registration_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'django_cfg_accounts'
        unique_together = ['user', 'source']
        verbose_name = "User Registration Source"
        verbose_name_plural = "User Registration Sources"
        ordering = ['-registration_date']


class CustomUser(AbstractUser):
    """Simplified user model for OTP-only authentication."""

    email = models.EmailField(unique=True)

    # Profile fields
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)

    # Profile metadata
    updated_at = models.DateTimeField(auto_now=True)

    # Managers
    objects: UserManager = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def is_admin(self) -> bool:
        return self.is_superuser

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return self.__class__.objects.get_full_name(self)

    @property
    def initials(self) -> str:
        """Get user's initials for avatar fallback."""
        return self.__class__.objects.get_initials(self)

    @property
    def display_username(self) -> str:
        """Get formatted username for display."""
        return self.__class__.objects.get_display_username(self)

    @property
    def unanswered_messages_count(self) -> int:
        """Get count of unanswered messages for the user."""
        return self.__class__.objects.get_unanswered_messages_count(self)

    def get_sources(self) -> List[RegistrationSource]:
        """Get all sources associated with this user."""
        return RegistrationSource.objects.filter(user_registration_sources__user=self)

    @property
    def primary_source(self) -> Optional[RegistrationSource]:
        """Get the first source where user registered."""
        user_source = self.get_sources().filter(first_registration=True).first()
        return user_source.source if user_source else None

    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = "User"
        verbose_name_plural = "Users"


class OTPSecret(models.Model):
    """Stores One-Time Passwords for authentication."""

    email = models.EmailField(db_index=True)
    secret = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_otp(length=6):
        """Generate random numeric OTP."""
        return "".join(random.choices(string.digits, k=length))

    @property
    def is_valid(self):
        """Check if OTP is still valid."""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_used(self):
        """Mark OTP as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"OTP for {self.email}"

    class Meta:
        app_label = 'django_cfg_accounts'
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "is_used", "expires_at"]),
        ]


class UserActivity(models.Model):
    """
    User activity log.
    """
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('otp_requested', 'OTP Requested'),
        ('otp_verified', 'OTP Verified'),
        ('profile_updated', 'Profile Updated'),
        ('registration', 'Registration'),
    ]
    
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Related objects (generic foreign key could be used here)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_type = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class TwilioResponse(models.Model):
    """Model for storing Twilio API responses and webhook data."""
    
    RESPONSE_TYPES = [
        ('api_send', 'API Send Request'),
        ('api_verify', 'API Verify Request'),
        ('webhook_status', 'Webhook Status Update'),
        ('webhook_delivery', 'Webhook Delivery Report'),
    ]
    
    SERVICE_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('voice', 'Voice'),
        ('email', 'Email'),
        ('verify', 'Verify API'),
    ]
    
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES)
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES)
    
    # Twilio identifiers
    message_sid = models.CharField(max_length=34, blank=True, help_text="Twilio Message SID")
    verification_sid = models.CharField(max_length=34, blank=True, help_text="Twilio Verification SID")
    
    # Request/Response data
    request_data = models.JSONField(default=dict, help_text="Original request parameters")
    response_data = models.JSONField(default=dict, help_text="Twilio API response")
    
    # Status and error handling
    status = models.CharField(max_length=20, blank=True, help_text="Message/Verification status")
    error_code = models.CharField(max_length=10, blank=True, help_text="Twilio error code")
    error_message = models.TextField(blank=True, help_text="Error description")
    
    # Contact information
    to_number = models.CharField(max_length=20, blank=True, help_text="Recipient phone/email")
    from_number = models.CharField(max_length=20, blank=True, help_text="Sender phone/email")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    price_unit = models.CharField(max_length=3, blank=True, help_text="Currency code")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    twilio_created_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp from Twilio")
    
    # Relations
    otp_secret = models.ForeignKey(
        'OTPSecret', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='twilio_responses',
        help_text="Related OTP if applicable"
    )
    
    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = 'Twilio Response'
        verbose_name_plural = 'Twilio Responses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['message_sid']),
            models.Index(fields=['verification_sid']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['response_type', 'service_type']),
        ]
    
    def __str__(self):
        return f"{self.get_response_type_display()} - {self.get_service_type_display()}"
    
    @property
    def has_error(self):
        """Check if response has error."""
        return bool(self.error_code or self.error_message)
    
    @property
    def is_successful(self):
        """Check if response is successful."""
        return not self.has_error and self.status in ['sent', 'delivered', 'approved']
