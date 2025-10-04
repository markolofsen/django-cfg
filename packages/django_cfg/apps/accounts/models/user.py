"""
User model and related functionality.
"""

from typing import Optional, List
from django.contrib.auth.models import AbstractUser
from django.db import models

from ..managers.user_manager import UserManager
from .base import user_avatar_path


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

    def get_sources(self) -> List['RegistrationSource']:
        """Get all sources associated with this user."""
        from .registration import RegistrationSource
        return RegistrationSource.objects.filter(user_registration_sources__user=self)

    @property
    def primary_source(self) -> Optional['RegistrationSource']:
        """Get the first source where user registered."""
        from .registration import UserRegistrationSource
        user_source = UserRegistrationSource.objects.filter(
            user=self, 
            first_registration=True
        ).first()
        return user_source.source if user_source else None

    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = "User"
        verbose_name_plural = "Users"
