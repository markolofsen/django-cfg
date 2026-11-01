"""
OAuth Connection Models

Links Django users to OAuth provider accounts (GitHub, Google, etc.)
"""

from django.db import models
from django.utils import timezone


class OAuthProvider(models.TextChoices):
    """Supported OAuth providers."""
    GITHUB = 'github', 'GitHub'
    GOOGLE = 'google', 'Google'


class OAuthConnection(models.Model):
    """
    Links a Django user to an OAuth provider account.

    Stores the connection between local user and external OAuth identity.
    A user can have multiple OAuth connections (e.g., GitHub + Google).

    Example:
        ```python
        # Check if user has GitHub connected
        has_github = user.oauth_connections.filter(provider='github').exists()

        # Get all connections for user
        connections = user.oauth_connections.all()
        ```
    """

    user = models.ForeignKey(
        'django_cfg_accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='oauth_connections',
        help_text="The Django user this OAuth account is linked to"
    )

    provider = models.CharField(
        max_length=20,
        choices=OAuthProvider.choices,
        db_index=True,
        help_text="OAuth provider name (github, google, etc.)"
    )

    # Provider-specific user data
    provider_user_id = models.CharField(
        max_length=255,
        help_text="Stable user id at the provider (GitHub numeric id, Google `sub`)"
    )

    provider_email = models.EmailField(
        blank=True,
        help_text="Email from OAuth provider (may differ from user.email)"
    )

    provider_username = models.CharField(
        max_length=100,
        blank=True,
        help_text="Username on the OAuth provider platform"
    )

    provider_avatar_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Avatar URL from OAuth provider"
    )

    provider_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Display name from OAuth provider"
    )

    # Token storage
    access_token = models.TextField(
        blank=True,
        help_text="OAuth access token (empty for Google: no Google API is called after sign-in)"
    )

    refresh_token = models.TextField(
        blank=True,
        help_text="OAuth refresh token (if available)"
    )

    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the access token expires"
    )

    # Metadata
    scopes = models.JSONField(
        default=list,
        blank=True,
        help_text="OAuth scopes granted"
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw user data from OAuth provider"
    )

    # Timestamps
    connected_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this OAuth connection was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this OAuth connection was last updated"
    )

    last_login_at = models.DateTimeField(
        default=timezone.now,
        help_text="Last time this OAuth connection was used for login"
    )

    class Meta:
        db_table = 'django_cfg_oauth_connection'
        verbose_name = 'OAuth Connection'
        verbose_name_plural = 'OAuth Connections'
        unique_together = [
            ('provider', 'provider_user_id'),  # One provider account = one connection
        ]
        indexes = [
            models.Index(fields=['provider', 'provider_user_id']),
            models.Index(fields=['user', 'provider']),
            models.Index(fields=['provider_email']),
        ]
        ordering = ['-connected_at']

    def __str__(self):
        return f"{self.user.email} → {self.get_provider_display()}:{self.provider_username or self.provider_user_id}"

    def update_last_login(self):
        """Update last_login_at timestamp."""
        self.last_login_at = timezone.now()
        self.save(update_fields=['last_login_at', 'updated_at'])

    def update_token(self, access_token: str, refresh_token: str = "", expires_at=None):
        """
        Update OAuth tokens.

        Args:
            access_token: New access token
            refresh_token: New refresh token (optional)
            expires_at: Token expiration datetime (optional)
        """
        self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        if expires_at:
            self.token_expires_at = expires_at
        self.save(update_fields=['access_token', 'refresh_token', 'token_expires_at', 'updated_at'])

    @property
    def is_token_expired(self) -> bool:
        """Check if access token is expired."""
        if not self.token_expires_at:
            return False
        return timezone.now() >= self.token_expires_at

    @classmethod
    def get_by_provider_id(cls, provider: str, provider_user_id: str):
        """
        Get OAuth connection by provider and provider user ID.

        Args:
            provider: Provider name (e.g., 'github')
            provider_user_id: User ID from provider

        Returns:
            OAuthConnection or None
        """
        return cls.objects.filter(
            provider=provider,
            provider_user_id=str(provider_user_id)
        ).select_related('user').first()

    @classmethod
    def get_user_connections(cls, user, provider: str = None):
        """
        Get all OAuth connections for a user.

        Args:
            user: Django user instance
            provider: Optional filter by provider

        Returns:
            QuerySet of OAuthConnection
        """
        qs = cls.objects.filter(user=user)
        if provider:
            qs = qs.filter(provider=provider)
        return qs


class OAuthState(models.Model):
    """
    One row per sign-in attempt: the CSRF ``state`` (primary key) and the
    server-side secrets of the attempt (PKCE verifier, nonce).

    A state is single use: ``OAuthService.consume_state`` deletes the row before
    anything else. Expired rows are purged by a scheduled job.
    """

    state = models.CharField(
        max_length=64,
        unique=True,
        primary_key=True,
        help_text="Random state token"
    )

    provider = models.CharField(
        max_length=20,
        choices=OAuthProvider.choices,
        help_text="OAuth provider"
    )

    redirect_uri = models.URLField(
        max_length=500,
        help_text="Redirect URI resolved at start; the token exchange reuses exactly this value"
    )

    code_verifier = models.CharField(
        max_length=128,
        blank=True,
        help_text="PKCE code verifier (server-side only; the challenge goes to the provider)"
    )

    nonce = models.CharField(
        max_length=64,
        blank=True,
        help_text="OIDC nonce the ID token must echo"
    )

    source_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Optional source URL for tracking"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this state was created"
    )

    expires_at = models.DateTimeField(
        help_text="When this state expires"
    )

    class Meta:
        db_table = 'django_cfg_oauth_state'
        verbose_name = 'OAuth State'
        verbose_name_plural = 'OAuth States'
        indexes = [
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.provider}:{self.state[:8]}..."

    @property
    def is_expired(self) -> bool:
        """Check if state is expired."""
        return timezone.now() >= self.expires_at

    @classmethod
    def cleanup_expired(cls):
        """Delete all expired states."""
        return cls.objects.filter(expires_at__lt=timezone.now()).delete()
