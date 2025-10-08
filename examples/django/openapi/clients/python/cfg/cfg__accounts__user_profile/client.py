from __future__ import annotations

import httpx

from .models import *


class CfgUserProfileAPI:
    """API endpoints for User Profile."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def profile_retrieve(self) -> User:
        """Get current user profile

    Retrieve the current authenticated user's profile information."""
        url = "/django_cfg_accounts/profile/"
        response = await self._client.get(url)
        response.raise_for_status()
        return User.model_validate(response.json())


    async def profile_avatar_create(self, data: InlineRequestBody) -> User:
        """Upload user avatar

    Upload avatar image for the current authenticated user. Accepts
    multipart/form-data with 'avatar' field."""
        url = "/django_cfg_accounts/profile/avatar/"
        response = await self._client.post(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return User.model_validate(response.json())


    async def profile_partial_update(self, data: UserProfileUpdateRequest) -> User:
        """Partial update user profile

    Partially update the current authenticated user's profile information.
    Supports avatar upload."""
        url = "/django_cfg_accounts/profile/partial/"
        response = await self._client.put(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return User.model_validate(response.json())


    async def profile_partial_partial_update(self, data: PatchedUserProfileUpdateRequest | None = None) -> User:
        """Partial update user profile

    Partially update the current authenticated user's profile information.
    Supports avatar upload."""
        url = "/django_cfg_accounts/profile/partial/"
        response = await self._client.patch(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return User.model_validate(response.json())


    async def profile_update_update(self, data: UserProfileUpdateRequest) -> User:
        """Update user profile

    Update the current authenticated user's profile information."""
        url = "/django_cfg_accounts/profile/update/"
        response = await self._client.put(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return User.model_validate(response.json())


    async def profile_update_partial_update(self, data: PatchedUserProfileUpdateRequest | None = None) -> User:
        """Update user profile

    Update the current authenticated user's profile information."""
        url = "/django_cfg_accounts/profile/update/"
        response = await self._client.patch(url, json=data.model_dump() if data else None)
        response.raise_for_status()
        return User.model_validate(response.json())


