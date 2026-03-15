from __future__ import annotations

import httpx

from .models import (
    BackupCodesRegenerateRequest,
    BackupCodesRegenerateResponse,
    BackupCodesStatus,
)


class CfgBackupCodesAPI:
    """API endpoints for Backup Codes."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def totp_backup_codes_retrieve(self) -> BackupCodesStatus:
        """
        Get backup codes status for user.
        """
        url = "/cfg/totp/backup-codes/"
        response = await self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return BackupCodesStatus.model_validate(response.json())


    async def totp_backup_codes_regenerate_create(
        self,
        data: BackupCodesRegenerateRequest,
    ) -> BackupCodesRegenerateResponse:
        """
        Regenerate backup codes. Requires TOTP code for verification.
        Invalidates all existing codes.
        """
        url = "/cfg/totp/backup-codes/regenerate/"
        response = await self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return BackupCodesRegenerateResponse.model_validate(response.json())


