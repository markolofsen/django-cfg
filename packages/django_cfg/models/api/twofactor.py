"""
Two-Factor Authentication Configuration Model.

Type-safe configuration for 2FA/TOTP using Pydantic v2.
"""

from typing import Literal

from pydantic import BaseModel, Field


class TwoFactorConfig(BaseModel):
    """
    Two-Factor Authentication configuration.

    Configures TOTP-based 2FA for the accounts app.

    Example:
        ```python
        from django_cfg import DjangoConfig
        from django_cfg.models.api.twofactor import TwoFactorConfig

        class MyConfig(DjangoConfig):
            two_factor: TwoFactorConfig = TwoFactorConfig(
                enabled=True,
                enforcement="optional",
            )
        ```

    Enforcement modes:
        - `optional`: Users can enable 2FA voluntarily
        - `encouraged`: Users are prompted to enable 2FA but not required
        - `required`: All users must have 2FA enabled
        - `admin_only`: Only staff/superusers must have 2FA
    """

    enabled: bool = Field(
        default=True,
        description="Enable 2FA system-wide",
    )

    enforcement: Literal["optional", "encouraged", "required", "admin_only"] = Field(
        default="optional",
        description="2FA enforcement policy",
    )

    session_lifetime_minutes: int = Field(
        default=5,
        ge=1,
        le=30,
        description="2FA verification session timeout in minutes",
    )

    max_failed_attempts: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Max failed 2FA attempts before session lockout",
    )

    grace_period_days: int = Field(
        default=7,
        ge=0,
        le=90,
        description="Days before 2FA becomes mandatory (if required)",
    )

    allow_totp: bool = Field(
        default=True,
        description="Allow TOTP (authenticator app) verification",
    )

    allow_backup_codes: bool = Field(
        default=True,
        description="Allow backup code verification",
    )

    backup_codes_count: int = Field(
        default=10,
        ge=5,
        le=20,
        description="Number of backup codes to generate",
    )

    issuer_name: str = Field(
        default="Django CFG",
        description="Issuer name shown in authenticator apps",
    )

    def get_settings_dict(self) -> dict:
        """
        Convert to Django settings dictionary.

        Returns:
            Dictionary with TOTP__ prefixed settings
        """
        return {
            "TOTP__ENABLED": self.enabled,
            "TOTP__ENFORCEMENT": self.enforcement,
            "TOTP__SESSION_LIFETIME_MINUTES": self.session_lifetime_minutes,
            "TOTP__MAX_FAILED_ATTEMPTS": self.max_failed_attempts,
            "TOTP__GRACE_PERIOD_DAYS": self.grace_period_days,
            "TOTP__ALLOW_TOTP": self.allow_totp,
            "TOTP__ALLOW_BACKUP_CODES": self.allow_backup_codes,
            "TOTP__BACKUP_CODES_COUNT": self.backup_codes_count,
            "TOTP__ISSUER_NAME": self.issuer_name,
        }


__all__ = ["TwoFactorConfig"]
