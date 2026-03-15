"""TOTP (Two-Factor Authentication) types re-exported from generated API.

Device management and backup codes types.
"""

from ..generated.cfg.cfg__totp__backup_codes.models import (
    BackupCodesRegenerateRequest,
    BackupCodesRegenerateResponse,
    BackupCodesStatus,
)
from ..generated.cfg.cfg__totp__totp_management.models import (
    DeviceList,
    DeviceListResponse,
    DisableRequest,
    PaginatedDeviceListResponseList,
)

__all__ = [
    # Devices
    "DeviceList",
    "DeviceListResponse",
    "PaginatedDeviceListResponseList",
    "DisableRequest",
    # Backup Codes
    "BackupCodesStatus",
    "BackupCodesRegenerateRequest",
    "BackupCodesRegenerateResponse",
]
