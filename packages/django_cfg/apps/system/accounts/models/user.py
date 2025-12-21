"""
User model and related functionality.
"""

from typing import List, Optional

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

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Get avatar URL with fallback to OAuth provider avatar.

        Priority:
        1. Local uploaded avatar
        2. GitHub/OAuth provider avatar
        3. None

        Returns:
            Avatar URL string or None
        """
        # 1. Local avatar
        if self.avatar:
            return self.avatar.url

        # 2. OAuth provider avatar
        try:
            oauth_connection = self.oauth_connections.filter(
                provider_avatar_url__isnull=False
            ).exclude(
                provider_avatar_url=''
            ).first()

            if oauth_connection:
                return oauth_connection.provider_avatar_url
        except Exception:
            pass

        return None

    # === 2FA Properties ===

    @property
    def has_2fa_enabled(self) -> bool:
        """
        Check if user has active 2FA device.

        Returns:
            True if user has at least one active TOTP device
        """
        from django_cfg.apps.system.totp.services import TOTPService

        return TOTPService.has_active_device(self)

    @property
    def requires_2fa(self) -> bool:
        """
        Check if 2FA is required for this user based on global policy.

        Returns:
            True if 2FA is required for this user
        """
        from .settings import TwoFactorSettings

        settings = TwoFactorSettings.get_settings()
        return settings.user_requires_2fa(self)

    @property
    def should_prompt_2fa(self) -> bool:
        """
        Check if user should be prompted to enable 2FA.

        Returns:
            True if user should be prompted
        """
        from .settings import TwoFactorSettings

        if self.has_2fa_enabled:
            return False

        settings = TwoFactorSettings.get_settings()
        return settings.user_should_prompt_2fa(self)

    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = "User"
        verbose_name_plural = "Users"
