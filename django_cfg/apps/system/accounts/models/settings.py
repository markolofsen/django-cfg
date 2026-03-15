"""
Two-Factor Authentication Settings.

Reads settings directly from DjangoConfig.two_factor.
No database storage needed - config.py is the single source of truth.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from django_cfg.apps.system.accounts.models import CustomUser


class TwoFactorEnforcement:
    """2FA enforcement policy options."""

    OPTIONAL = "optional"
    ENCOURAGED = "encouraged"
    REQUIRED = "required"
    ADMIN_ONLY = "admin_only"


class TwoFactorSettings:
    """
    2FA settings reader from DjangoConfig.

    This is NOT a Django model - it reads directly from config.py.
    Single source of truth: DjangoConfig.two_factor
    """

    def __init__(self):
        self._config = self._get_config()

    @staticmethod
    def _get_config():
        """Get TwoFactorConfig from DjangoConfig."""
        try:
            from django_cfg.core.config import get_current_config

            config = get_current_config()
            return config.two_factor if config else None
        except Exception:
            return None

    @classmethod
    def get_settings(cls) -> "TwoFactorSettings":
        """Get settings instance (for compatibility with existing code)."""
        return cls()

    @property
    def enabled(self) -> bool:
        """Check if 2FA is enabled."""
        return self._config.enabled if self._config else False

    @property
    def enforcement(self) -> str:
        """Get enforcement policy."""
        return self._config.enforcement if self._config else TwoFactorEnforcement.OPTIONAL

    @property
    def grace_period_days(self) -> int:
        """Get grace period in days."""
        return self._config.grace_period_days if self._config else 7

    @property
    def session_lifetime_minutes(self) -> int:
        """Get session lifetime in minutes."""
        return self._config.session_lifetime_minutes if self._config else 5

    @property
    def max_failed_attempts(self) -> int:
        """Get max failed attempts."""
        return self._config.max_failed_attempts if self._config else 5

    @property
    def allow_totp(self) -> bool:
        """Check if TOTP is allowed."""
        return self._config.allow_totp if self._config else True

    @property
    def allow_backup_codes(self) -> bool:
        """Check if backup codes are allowed."""
        return self._config.allow_backup_codes if self._config else True

    def user_requires_2fa(self, user: "CustomUser") -> bool:
        """
        Check if 2FA is required for a specific user.

        Args:
            user: User instance to check

        Returns:
            True if 2FA is required for this user
        """
        if not self.enabled:
            return False

        if self.enforcement == TwoFactorEnforcement.REQUIRED:
            return True

        if self.enforcement == TwoFactorEnforcement.ADMIN_ONLY:
            return user.is_staff or user.is_superuser

        return False

    def user_should_prompt_2fa(self, user: "CustomUser") -> bool:
        """
        Check if user should be prompted to enable 2FA.

        Args:
            user: User instance to check

        Returns:
            True if user should be prompted to enable 2FA
        """
        if not self.enabled:
            return False

        # Already has 2FA? Don't prompt
        if user.has_2fa_enabled:
            return False

        if self.enforcement in [
            TwoFactorEnforcement.ENCOURAGED,
            TwoFactorEnforcement.REQUIRED,
            TwoFactorEnforcement.ADMIN_ONLY,
        ]:
            # For admin_only, only prompt staff/superusers
            if self.enforcement == TwoFactorEnforcement.ADMIN_ONLY:
                return user.is_staff or user.is_superuser
            return True

        return False
