"""
OAuth Serializers

Request/Response serializers for OAuth authentication endpoints.
"""

from rest_framework import serializers

from ..models.oauth import OAuthConnection, OAuthProvider


class OAuthAuthorizeRequestSerializer(serializers.Serializer):
    """Request to start OAuth flow."""

    redirect_uri = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="URL to redirect after OAuth authorization. If not provided, uses config's site_url + callback_path"
    )

    source_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Optional source URL for registration tracking"
    )


class OAuthAuthorizeResponseSerializer(serializers.Serializer):
    """Response with OAuth authorization URL."""

    authorization_url = serializers.URLField(
        help_text="Full URL to redirect user to OAuth provider"
    )

    state = serializers.CharField(
        help_text="State token for CSRF protection. Store this and verify on callback."
    )


class OAuthCallbackRequestSerializer(serializers.Serializer):
    """Request to complete OAuth flow (callback handler)."""

    code = serializers.CharField(
        min_length=10,
        max_length=500,
        help_text="Authorization code from OAuth provider callback"
    )

    state = serializers.CharField(
        min_length=20,
        max_length=100,
        help_text="State token for CSRF verification (from authorize response)"
    )

    redirect_uri = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Same redirect_uri used in authorize request. If not provided, uses config's site_url + callback_path"
    )


class OAuthTokenResponseSerializer(serializers.Serializer):
    """
    Response with JWT tokens after OAuth authentication.

    When 2FA is required:
    - requires_2fa: True
    - session_id: UUID of 2FA verification session
    - access/refresh/user: null

    When 2FA is not required:
    - requires_2fa: False
    - session_id: null
    - access/refresh/user: populated
    """

    requires_2fa = serializers.BooleanField(
        default=False,
        help_text="True if 2FA verification is required"
    )

    session_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text="2FA session ID (only when requires_2fa=True)"
    )

    access = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="JWT access token (null when requires_2fa=True)"
    )

    refresh = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="JWT refresh token (null when requires_2fa=True)"
    )

    user = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Authenticated user info (null when requires_2fa=True)"
    )

    is_new_user = serializers.BooleanField(
        help_text="True if a new user was created during this OAuth flow"
    )

    is_new_connection = serializers.BooleanField(
        help_text="True if a new OAuth connection was created"
    )

    should_prompt_2fa = serializers.BooleanField(
        required=False,
        help_text="True if user should be prompted to enable 2FA"
    )


class OAuthConnectionSerializer(serializers.ModelSerializer):
    """Serializer for OAuth connection info (user-facing)."""

    provider_display = serializers.CharField(
        source='get_provider_display',
        read_only=True
    )

    class Meta:
        model = OAuthConnection
        fields = [
            'id',
            'provider',
            'provider_display',
            'provider_username',
            'provider_email',
            'provider_avatar_url',
            'connected_at',
            'last_login_at',
        ]
        read_only_fields = fields


class OAuthProvidersResponseSerializer(serializers.Serializer):
    """Response with available OAuth providers."""

    providers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of available OAuth providers"
    )


class OAuthDisconnectRequestSerializer(serializers.Serializer):
    """Request to disconnect OAuth provider."""

    provider = serializers.ChoiceField(
        choices=OAuthProvider.choices,
        help_text="OAuth provider to disconnect"
    )


class OAuthErrorSerializer(serializers.Serializer):
    """Error response for OAuth endpoints."""

    error = serializers.CharField(
        help_text="Error code"
    )

    error_description = serializers.CharField(
        required=False,
        help_text="Human-readable error description"
    )
