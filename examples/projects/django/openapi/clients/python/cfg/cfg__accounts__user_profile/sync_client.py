from __future__ import annotations

import httpx

from .models import *


class SyncCfgUserProfileAPI:
    """Synchronous API endpoints for User Profile."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def accounts_profile_retrieve(self) -> User:
        """
        Get current user profile

        Retrieve the current authenticated user's profile information.
        """
        url = "/cfg/accounts/profile/"
        response = self._client.get(url)
        response.raise_for_status()
        return User.model_validate(response.json())


    def accounts_profile_avatar_create(self, data: InlineRequestBody) -> User:
        """
        Upload user avatar

        Upload avatar image for the current authenticated user. Accepts
        multipart/form-data with 'avatar' field.
        """
        url = "/cfg/accounts/profile/avatar/"
        response = self._client.post(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return User.model_validate(response.json())


    def accounts_profile_partial_update(self, data: UserProfileUpdateRequest) -> User:
        """
        Partial update user profile

        Partially update the current authenticated user's profile information.
        Supports avatar upload.
        """
        url = "/cfg/accounts/profile/partial/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return User.model_validate(response.json())


    def accounts_profile_partial_partial_update(self, data: PatchedUserProfileUpdateRequest | None = None) -> User:
        """
        Partial update user profile

        Partially update the current authenticated user's profile information.
        Supports avatar upload.
        """
        url = "/cfg/accounts/profile/partial/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return User.model_validate(response.json())


    def accounts_profile_update_update(self, data: UserProfileUpdateRequest) -> User:
        """
        Update user profile

        Update the current authenticated user's profile information.
        """
        url = "/cfg/accounts/profile/update/"
        response = self._client.put(url, json=data.model_dump(exclude_unset=True))
        response.raise_for_status()
        return User.model_validate(response.json())


    def accounts_profile_update_partial_update(self, data: PatchedUserProfileUpdateRequest | None = None) -> User:
        """
        Update user profile

        Update the current authenticated user's profile information.
        """
        url = "/cfg/accounts/profile/update/"
        response = self._client.patch(url, json=data.model_dump(exclude_unset=True) if data is not None else None)
        response.raise_for_status()
        return User.model_validate(response.json())


