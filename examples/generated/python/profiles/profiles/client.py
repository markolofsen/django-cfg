from __future__ import annotations

import httpx

from .models import *


class ProfilesProfilesAPI:
    """API endpoints for Profiles."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize sub-client with shared httpx client."""
        self._client = client

    async def profiles_list(self, page: int | None = None, page_size: int | None = None) -> list[PaginatedUserProfileList]:
        """
        List user profiles

        Get a paginated list of all user profiles
        """
        url = "/profiles/profiles/"
        response = await self._client.get(url, params={"page": page if page is not None else None, "page_size": page_size if page_size is not None else None})
        response.raise_for_status()
        data = response.json()
        return [PaginatedUserProfileList.model_validate(item) for item in data.get("results", [])]


    async def profiles_create(self, data: UserProfileRequest) -> UserProfile:
        """
        Create user profile

        Create a new user profile
        """
        url = "/profiles/profiles/"
        response = await self._client.post(url, json=data.model_dump())
        response.raise_for_status()
        return UserProfile.model_validate(response.json())


    async def profiles_retrieve(self, id: int) -> UserProfile:
        """
        Get user profile

        Get detailed information about a specific user profile
        """
        url = f"/profiles/profiles/{id}/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserProfile.model_validate(response.json())


    async def profiles_update(self, id: int, data: UserProfileUpdateRequest) -> UserProfileUpdate:
        """
        Update user profile

        Update user profile information
        """
        url = f"/profiles/profiles/{id}/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return UserProfileUpdate.model_validate(response.json())


    async def profiles_partial_update(self, id: int, data: PatchedUserProfileUpdateRequest | None = None) -> UserProfileUpdate:
        """
        Partially update user profile

        Partially update user profile information
        """
        url = f"/profiles/profiles/{id}/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return UserProfileUpdate.model_validate(response.json())


    async def profiles_destroy(self, id: int) -> None:
        """
        Delete user profile

        Delete a user profile
        """
        url = f"/profiles/profiles/{id}/"
        response = await self._client.delete(url)
        response.raise_for_status()
        return None


    async def profiles_me_retrieve(self) -> UserProfile:
        """
        Get my profile

        Get current user's profile
        """
        url = "/profiles/profiles/me/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserProfile.model_validate(response.json())


    async def profiles_me_update(self, data: UserProfileRequest) -> UserProfile:
        """
        Get my profile

        Get current user's profile
        """
        url = "/profiles/profiles/me/"
        response = await self._client.put(url, json=data.model_dump())
        response.raise_for_status()
        return UserProfile.model_validate(response.json())


    async def profiles_me_partial_update(self, data: PatchedUserProfileRequest | None = None) -> UserProfile:
        """
        Get my profile

        Get current user's profile
        """
        url = "/profiles/profiles/me/"
        response = await self._client.patch(url, json=data.model_dump() if data is not None else None)
        response.raise_for_status()
        return UserProfile.model_validate(response.json())


    async def profiles_stats_retrieve(self) -> UserProfileStats:
        """
        Get profile statistics

        Get comprehensive profile statistics
        """
        url = "/profiles/profiles/stats/"
        response = await self._client.get(url)
        response.raise_for_status()
        return UserProfileStats.model_validate(response.json())


