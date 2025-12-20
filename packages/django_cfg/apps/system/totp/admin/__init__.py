"""
Admin interface for TOTP 2FA models.

Modular admin configuration with declarative PydanticAdmin.
"""

from .backup_admin import BackupCodeAdmin
from .config import backupcode_config, totpdevice_config, twofactorsession_config
from .device_admin import TOTPDeviceAdmin, disable_devices, enable_devices
from .session_admin import TwoFactorSessionAdmin, cleanup_expired_action

__all__ = [
    "BackupCodeAdmin",
    "TOTPDeviceAdmin",
    "TwoFactorSessionAdmin",
    "backupcode_config",
    "totpdevice_config",
    "twofactorsession_config",
    "disable_devices",
    "enable_devices",
    "cleanup_expired_action",
]
