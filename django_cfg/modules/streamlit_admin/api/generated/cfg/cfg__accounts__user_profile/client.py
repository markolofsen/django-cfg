from __future__ import annotations

import httpx

from .models import (
    AccountDeleteResponse,
    CfgAccountsProfileAvatarCreateRequest,
    PatchedUserProfileUpdateRequest,
    User,
    UserProfileUpdateRequest,
)


class CfgUserProfileAPI:
    """API endpoints for User Profile."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def accounts_profile_retrieve(self) -> User:
        """
        Get current user profile

        Retrieve the current authenticated user's profile information.
        """
        url = "/cfg/accounts/profile/"
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
        return User.model_validate(response.json())


    async def accounts_profile_avatar_create(
        self,
        data: CfgAccountsProfileAvatarCreateRequest,
    ) -> User:
        """
        Upload user avatar

        Upload avatar image for the current authenticated user. Accepts
        multipart/form-data with 'avatar' field.
        """
        url = "/cfg/accounts/profile/avatar/"
        # Build multipart form data
        _files = {}
        _form_data = {}
        _raw_data = data.model_dump(mode="json", exclude_unset=True, exclude_none=True)
        if 'avatar' in _raw_data and _raw_data['avatar'] is not None:
            _files['avatar'] = _raw_data['avatar']
        response = await self._client.post(url, files=_files if _files else None, data=_form_data if _form_data else None)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return User.model_validate(response.json())


    async def accounts_profile_delete_create(self) -> AccountDeleteResponse:
        """
        Delete user account

        Permanently delete the current user's account. This operation: -
        Deactivates the account (user cannot log in) - Anonymizes personal data
        (GDPR compliance) - Frees up the email address for re-registration -
        Preserves audit trail The account can be restored by an administrator if
        needed.
        """
        url = "/cfg/accounts/profile/delete/"
        response = await self._client.post(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return AccountDeleteResponse.model_validate(response.json())


    async def accounts_profile_partial_update(self, data: UserProfileUpdateRequest) -> User:
        """
        Partial update user profile

        Partially update the current authenticated user's profile information.
        Supports avatar upload.
        """
        url = "/cfg/accounts/profile/partial/"
        response = await self._client.put(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return User.model_validate(response.json())


    async def accounts_profile_partial_partial_update(
        self,
        data: PatchedUserProfileUpdateRequest | None = None,
    ) -> User:
        """
        Partial update user profile

        Partially update the current authenticated user's profile information.
        Supports avatar upload.
        """
        url = "/cfg/accounts/profile/partial/"
        _json = data.model_dump(mode="json", exclude_unset=True, exclude_none=True) if data else None
        response = await self._client.patch(url, json=_json)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return User.model_validate(response.json())


    async def accounts_profile_update_update(self, data: UserProfileUpdateRequest) -> User:
        """
        Update user profile

        Update the current authenticated user's profile information.
        """
        url = "/cfg/accounts/profile/update/"
        response = await self._client.put(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return User.model_validate(response.json())


    async def accounts_profile_update_partial_update(
        self,
        data: PatchedUserProfileUpdateRequest | None = None,
    ) -> User:
        """
        Update user profile

        Update the current authenticated user's profile information.
        """
        url = "/cfg/accounts/profile/update/"
        _json = data.model_dump(mode="json", exclude_unset=True, exclude_none=True) if data else None
        response = await self._client.patch(url, json=_json)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return User.model_validate(response.json())


