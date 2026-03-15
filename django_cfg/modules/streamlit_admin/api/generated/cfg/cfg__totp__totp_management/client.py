from __future__ import annotations

import httpx

from .models import (
    DisableRequest,
    PaginatedDeviceListResponseList,
)


class CfgTotpManagementAPI:
    """API endpoints for TOTP Management."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def totp_devices_list(
        self,
        ordering: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        search: str | None = None,
    ) -> list[PaginatedDeviceListResponseList]:
        """
        List all TOTP devices for user.
        """
        url = "/cfg/totp/devices/"
        _params = {
            k: v for k, v in {
                "ordering": ordering,
                "page": page,
                "page_size": page_size,
                "search": search,
            }.items() if v is not None
        }
        response = await self._client.get(url, params=_params)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return PaginatedDeviceListResponseList.model_validate(response.json())


    async def totp_disable_create(self, data: DisableRequest) -> None:
        """
        Completely disable 2FA for account. Requires verification code.
        """
        url = "/cfg/totp/disable/"
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
        return None


