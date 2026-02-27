from __future__ import annotations

import httpx

from .models import (
    OAuthAuthorizeRequestRequest,
    OAuthAuthorizeResponse,
    OAuthCallbackRequestRequest,
    OAuthConnection,
    OAuthDisconnectRequestRequest,
    OAuthError,
    OAuthProvidersResponse,
    OAuthTokenResponse,
)


class SyncCfgOauthAPI:
    """Synchronous API endpoints for Oauth."""

    def __init__(self, client: httpx.Client):
        """Initialize sync sub-client with shared httpx client."""
        self._client = client

    def accounts_oauth_connections_list(self) -> list[OAuthConnection]:
        """
        List OAuth connections

        Get all OAuth connections for the current user.
        """
        url = "/cfg/accounts/oauth/connections/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return [OAuthConnection.model_validate(item) for item in response.json()]


    def accounts_oauth_disconnect_create(self, data: OAuthDisconnectRequestRequest) -> None:
        """
        Disconnect OAuth provider

        Remove OAuth connection for the specified provider.
        """
        url = "/cfg/accounts/oauth/disconnect/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )


    def accounts_oauth_github_authorize_create(
        self,
        data: OAuthAuthorizeRequestRequest,
    ) -> OAuthAuthorizeResponse:
        """
        Start GitHub OAuth

        Generate GitHub OAuth authorization URL. Redirect user to this URL to
        start authentication.
        """
        url = "/cfg/accounts/oauth/github/authorize/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return OAuthAuthorizeResponse.model_validate(response.json())


    def accounts_oauth_github_callback_create(
        self,
        data: OAuthCallbackRequestRequest,
    ) -> OAuthTokenResponse:
        """
        Complete GitHub OAuth

        Exchange authorization code for JWT tokens. Call this after GitHub
        redirects back with code.
        """
        url = "/cfg/accounts/oauth/github/callback/"
        response = self._client.post(url, json=data.model_dump(mode="json", exclude_unset=True, exclude_none=True))
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return OAuthTokenResponse.model_validate(response.json())


    def accounts_oauth_providers_retrieve(self) -> OAuthProvidersResponse:
        """
        List OAuth providers

        Get list of available OAuth providers for authentication.
        """
        url = "/cfg/accounts/oauth/providers/"
        response = self._client.get(url)
        if not response.is_success:
            try:
                error_body = response.json()
            except Exception:
                error_body = response.text
            msg = f"{response.status_code}: {error_body}"
            raise httpx.HTTPStatusError(
                msg, request=response.request, response=response
            )
        return OAuthProvidersResponse.model_validate(response.json())


