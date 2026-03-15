"""
Django CFG Two-Factor Authentication (2FA/TOTP) App.

Provides TOTP-based two-factor authentication for Django applications.
Can be used independently or integrated with django-cfg accounts flow.

Features:
- TOTP device management (setup, verify, disable)
- Backup recovery codes
- Session-based 2FA verification
- QR code generation for authenticator apps
- Configurable enforcement policies

Usage:
    # Independent usage
    from django_cfg.apps.system.totp.services import TOTPService

    # Setup 2FA for user
    device = TOTPService.create_device(user)
    qr_uri = TOTPService.get_provisioning_uri(device)

    # Verify code
    is_valid = TOTPService.verify_code(device, "123456")

    # Integration with DjangoConfig
    class MyConfig(DjangoConfig):
        two_factor: TwoFactorConfig = TwoFactorConfig(
            enabled=True,
            issuer_name="My App",
            enforce_for_staff=True,
        )
"""

default_app_config = "django_cfg.apps.system.totp.apps.TOTPConfig"

__all__ = [
    "default_app_config",
]
