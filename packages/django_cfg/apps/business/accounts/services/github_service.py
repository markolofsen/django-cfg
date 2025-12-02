"""
GitHub OAuth Service

Handles the complete GitHub OAuth authentication flow:
1. Generate authorization URL with state
2. Exchange authorization code for access token
3. Fetch user info from GitHub API
4. Create or link Django user
"""

import logging
import secrets
from datetime import timedelta
from typing import Optional, Tuple
from urllib.parse import urlencode

import httpx
from django.db import transaction
from django.utils import timezone

from django_cfg.modules.django_telegram import DjangoTelegram

from ..models import CustomUser
from ..models.oauth import OAuthConnection, OAuthProvider, OAuthState

logger = logging.getLogger(__name__)


class GitHubOAuthError(Exception):
    """GitHub OAuth specific error."""
    pass


class GitHubOAuthService:
    """
    GitHub OAuth authentication service.

    Handles the complete OAuth 2.0 flow for GitHub authentication,
    including user creation and account linking.

    Usage:
        ```python
        # 1. Start OAuth flow
        url, state = GitHubOAuthService.get_authorization_url(
            redirect_uri="https://app.com/callback"
        )

        # 2. After callback, exchange code
        token_data = await GitHubOAuthService.exchange_code(code, redirect_uri)

        # 3. Get user and authenticate
        user, created = GitHubOAuthService.authenticate(
            code=code,
            state=state,
            redirect_uri=redirect_uri
        )
        ```
    """

    PROVIDER = OAuthProvider.GITHUB

    @classmethod
    def _get_config(cls):
        """
        Get GitHub OAuth config from Django settings.

        Returns:
            GitHubOAuthConfig or None
        """
        from django.conf import settings
        return getattr(settings, 'GITHUB_OAUTH_CONFIG', None)

    @classmethod
    def is_enabled(cls) -> bool:
        """
        Check if GitHub OAuth is enabled and configured.

        Returns:
            True if GitHub OAuth is ready to use
        """
        config = cls._get_config()
        return config is not None and config.is_configured()

    @classmethod
    def generate_state(cls) -> str:
        """
        Generate a secure random state token for CSRF protection.

        Returns:
            Random 43-character URL-safe string
        """
        return secrets.token_urlsafe(32)

    @classmethod
    @transaction.atomic
    def get_authorization_url(
        cls,
        redirect_uri: str,
        source_url: str = ""
    ) -> Tuple[str, str]:
        """
        Generate GitHub OAuth authorization URL.

        Args:
            redirect_uri: URL GitHub will redirect to after authorization
            source_url: Optional source URL for registration tracking

        Returns:
            Tuple of (authorization_url, state_token)

        Raises:
            GitHubOAuthError: If GitHub OAuth is not configured
        """
        config = cls._get_config()
        if not config or not config.is_configured():
            raise GitHubOAuthError("GitHub OAuth is not configured")

        # Generate and store state
        state = cls.generate_state()
        expires_at = timezone.now() + timedelta(seconds=config.state_timeout_seconds)

        OAuthState.objects.create(
            state=state,
            provider=cls.PROVIDER,
            redirect_uri=redirect_uri,
            source_url=source_url,
            expires_at=expires_at,
        )

        # Build authorization URL
        params = {
            'client_id': config.client_id,
            'redirect_uri': redirect_uri,
            'scope': config.get_scope_string(),
            'state': state,
        }

        authorization_url = f"{config.authorize_url}?{urlencode(params)}"

        logger.info(f"Generated GitHub OAuth URL with state: {state[:8]}...")
        return authorization_url, state

    @classmethod
    def verify_state(cls, state: str, redirect_uri: str) -> Optional[OAuthState]:
        """
        Verify OAuth state token.

        Args:
            state: State token from callback
            redirect_uri: Redirect URI to verify

        Returns:
            OAuthState if valid, None otherwise
        """
        try:
            oauth_state = OAuthState.objects.get(
                state=state,
                provider=cls.PROVIDER,
            )

            if oauth_state.is_expired:
                logger.warning(f"OAuth state expired: {state[:8]}...")
                oauth_state.delete()
                return None

            if oauth_state.redirect_uri != redirect_uri:
                logger.warning(f"OAuth redirect_uri mismatch for state: {state[:8]}...")
                return None

            return oauth_state

        except OAuthState.DoesNotExist:
            logger.warning(f"OAuth state not found: {state[:8]}...")
            return None

    @classmethod
    async def exchange_code_for_token(cls, code: str, redirect_uri: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub callback
            redirect_uri: Same redirect_uri used in authorization

        Returns:
            Dict with access_token, token_type, scope

        Raises:
            GitHubOAuthError: If token exchange fails
        """
        config = cls._get_config()
        if not config:
            raise GitHubOAuthError("GitHub OAuth is not configured")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                config.token_url,
                data={
                    'client_id': config.client_id,
                    'client_secret': config.client_secret,
                    'code': code,
                    'redirect_uri': redirect_uri,
                },
                headers={
                    'Accept': 'application/json',
                },
            )

            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.status_code}")
                raise GitHubOAuthError(f"Token exchange failed: {response.status_code}")

            data = response.json()

            if 'error' in data:
                error_desc = data.get('error_description', data['error'])
                logger.error(f"GitHub OAuth error: {error_desc}")
                raise GitHubOAuthError(error_desc)

            logger.info("GitHub token exchange successful")
            return data

    @classmethod
    async def get_github_user(cls, access_token: str) -> dict:
        """
        Fetch user info from GitHub API.

        Args:
            access_token: GitHub access token

        Returns:
            GitHub user data dict with id, login, email, name, avatar_url

        Raises:
            GitHubOAuthError: If API request fails
        """
        config = cls._get_config()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'X-GitHub-Api-Version': '2022-11-28',
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get user profile
            user_response = await client.get(config.user_api_url, headers=headers)

            if user_response.status_code != 200:
                logger.error(f"GitHub user API failed: {user_response.status_code}")
                raise GitHubOAuthError(f"Failed to fetch user info: {user_response.status_code}")

            user_data = user_response.json()

            # Get primary email if not public
            if not user_data.get('email'):
                emails_response = await client.get(config.emails_api_url, headers=headers)
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    # Find primary verified email
                    primary_email = next(
                        (e['email'] for e in emails if e.get('primary') and e.get('verified')),
                        None
                    )
                    if primary_email:
                        user_data['email'] = primary_email
                    elif emails:
                        # Fallback to first verified email
                        verified_email = next(
                            (e['email'] for e in emails if e.get('verified')),
                            None
                        )
                        if verified_email:
                            user_data['email'] = verified_email

            logger.info(f"Fetched GitHub user: {user_data.get('login')}")
            return user_data

    @classmethod
    @transaction.atomic
    def authenticate_or_create_user(
        cls,
        github_user: dict,
        access_token: str,
        scopes: list = None,
        source_url: str = ""
    ) -> Tuple[CustomUser, bool, bool]:
        """
        Authenticate via GitHub or create new user.

        Logic:
        1. If OAuth connection exists → return linked user
        2. If user with same email exists → link OAuth and return user
        3. Otherwise → create new user and OAuth connection

        Args:
            github_user: User data from GitHub API
            access_token: GitHub access token
            scopes: OAuth scopes granted
            source_url: Optional source URL for tracking

        Returns:
            Tuple of (user, user_created, connection_created)
        """
        config = cls._get_config()

        github_id = str(github_user['id'])
        github_email = github_user.get('email', '')
        github_username = github_user.get('login', '')
        github_avatar = github_user.get('avatar_url', '')
        github_name = github_user.get('name', '')

        # 1. Check for existing OAuth connection
        existing_connection = OAuthConnection.get_by_provider_id(
            provider=cls.PROVIDER,
            provider_user_id=github_id
        )

        if existing_connection:
            # Update token and last login
            existing_connection.update_token(access_token)
            existing_connection.update_last_login()

            logger.info(f"GitHub OAuth login for existing user: {existing_connection.user.email}")

            # Send Telegram notification
            cls._notify_login(existing_connection.user, is_new=False)

            return existing_connection.user, False, False

        # 2. Check for existing user with same email (if linking allowed)
        user = None
        user_created = False

        if github_email and config.allow_account_linking:
            user = CustomUser.objects.filter(email__iexact=github_email).first()
            if user:
                logger.info(f"Linking GitHub to existing user: {user.email}")

        # 3. Create new user if needed (if auto-create allowed)
        if not user:
            if not config.auto_create_user:
                raise GitHubOAuthError("User not found and auto-creation is disabled")

            # Generate email if not provided
            email = github_email or f"{github_username}@github.local"

            user, user_created = CustomUser.objects.register_user(
                email=email,
                source_url=source_url
            )

            # Update user profile from GitHub
            if github_name:
                parts = github_name.split(' ', 1)
                user.first_name = parts[0]
                if len(parts) > 1:
                    user.last_name = parts[1]

            if github_username and (not user.username or user.username.startswith('user_')):
                # Only update if username is auto-generated
                user.username = github_username

            user.save()

            logger.info(f"Created new user from GitHub: {user.email}")

        # 4. Create OAuth connection
        OAuthConnection.objects.create(
            user=user,
            provider=cls.PROVIDER,
            provider_user_id=github_id,
            provider_email=github_email,
            provider_username=github_username,
            provider_avatar_url=github_avatar,
            provider_name=github_name,
            access_token=access_token,
            scopes=scopes or [],
            raw_data=github_user,
        )

        logger.info(f"Created GitHub OAuth connection for: {user.email}")

        # Send Telegram notification
        cls._notify_login(user, is_new=user_created, github_username=github_username)

        return user, user_created, True

    @classmethod
    def _notify_login(cls, user: CustomUser, is_new: bool, github_username: str = ""):
        """Send Telegram notification for OAuth login."""
        try:
            notification_data = {
                "Email": user.email,
                "GitHub Username": github_username or "N/A",
                "User Type": "New User" if is_new else "Existing User",
                "Login Time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            }

            if is_new:
                DjangoTelegram.send_success("New User via GitHub OAuth", notification_data)
            else:
                DjangoTelegram.send_info("GitHub OAuth Login", notification_data)

        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")

    @classmethod
    def cleanup_expired_states(cls) -> int:
        """
        Clean up expired OAuth states.

        Returns:
            Number of deleted states
        """
        deleted, _ = OAuthState.cleanup_expired()
        if deleted:
            logger.info(f"Cleaned up {deleted} expired OAuth states")
        return deleted
