"""
OAuth Views

REST API endpoints for OAuth authentication flow.
"""

import asyncio
import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django_cfg.apps.system.totp.services import TOTPService, TwoFactorSessionService
from django_cfg.modules.base import BaseCfgModule

from ..models.oauth import OAuthConnection
from ..serializers.oauth import (
    OAuthAuthorizeRequestSerializer,
    OAuthAuthorizeResponseSerializer,
    OAuthCallbackRequestSerializer,
    OAuthConnectionSerializer,
    OAuthDisconnectRequestSerializer,
    OAuthErrorSerializer,
    OAuthProvidersResponseSerializer,
    OAuthTokenResponseSerializer,
)
from ..services.github_service import GitHubOAuthError, GitHubOAuthService

logger = logging.getLogger(__name__)


@extend_schema(tags=['OAuth'])
class OAuthProvidersView(APIView):
    """
    List available OAuth providers.

    Returns list of OAuth providers that are enabled and configured.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        responses={200: OAuthProvidersResponseSerializer},
        summary="List OAuth providers",
        description="Get list of available OAuth providers for authentication.",
    )
    def get(self, request):
        providers = []

        if GitHubOAuthService.is_enabled():
            providers.append({
                'id': 'github',
                'name': 'GitHub',
                'icon': 'github',
            })

        # Future providers would be added here

        return Response({
            'providers': providers,
        })


@extend_schema_view(
    post=extend_schema(
        tags=['OAuth'],
        request=OAuthAuthorizeRequestSerializer,
        responses={
            200: OAuthAuthorizeResponseSerializer,
            503: OAuthErrorSerializer,
        },
        summary="Start GitHub OAuth",
        description="Generate GitHub OAuth authorization URL. Redirect user to this URL to start authentication.",
    )
)
class GitHubAuthorizeView(APIView):
    """
    Start GitHub OAuth flow.

    Returns authorization URL and state token.
    Frontend should redirect user to the authorization URL,
    then handle the callback with the code and state.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OAuthAuthorizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not GitHubOAuthService.is_enabled():
            return Response(
                {
                    'error': 'github_oauth_disabled',
                    'error_description': 'GitHub OAuth is not enabled',
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            # Get redirect_uri from request or auto-generate from config
            redirect_uri = serializer.validated_data.get('redirect_uri')
            if not redirect_uri:
                config = GitHubOAuthService._get_config()
                if config:
                    redirect_uri = config.get_redirect_uri(provider="github")
                if not redirect_uri:
                    return Response(
                        {
                            'error': 'missing_redirect_uri',
                            'error_description': 'redirect_uri not provided and site_url not configured',
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            source_url = serializer.validated_data.get('source_url', '')

            authorization_url, state = GitHubOAuthService.get_authorization_url(
                redirect_uri=redirect_uri,
                source_url=source_url,
            )

            return Response({
                'authorization_url': authorization_url,
                'state': state,
            })

        except GitHubOAuthError as e:
            logger.error(f"GitHub OAuth authorize error: {e}")
            return Response(
                {
                    'error': 'oauth_error',
                    'error_description': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    post=extend_schema(
        tags=['OAuth'],
        request=OAuthCallbackRequestSerializer,
        responses={
            200: OAuthTokenResponseSerializer,
            400: OAuthErrorSerializer,
        },
        summary="Complete GitHub OAuth",
        description="Exchange authorization code for JWT tokens. Call this after GitHub redirects back with code.",
    )
)
class GitHubCallbackView(APIView):
    """
    Handle GitHub OAuth callback.

    Exchanges authorization code for access token, fetches user info,
    creates/links user account, and returns JWT tokens.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = OAuthCallbackRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        state = serializer.validated_data['state']

        # Get redirect_uri from request or auto-generate from config
        redirect_uri = serializer.validated_data.get('redirect_uri')
        if not redirect_uri:
            config = GitHubOAuthService._get_config()
            if config:
                redirect_uri = config.get_redirect_uri(provider="github")
            if not redirect_uri:
                return Response(
                    {
                        'error': 'missing_redirect_uri',
                        'error_description': 'redirect_uri not provided and site_url not configured',
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Verify state
        oauth_state = GitHubOAuthService.verify_state(state, redirect_uri)
        if not oauth_state:
            return Response(
                {
                    'error': 'invalid_state',
                    'error_description': 'Invalid or expired state token',
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        source_url = oauth_state.source_url

        # Delete used state
        oauth_state.delete()

        try:
            # Run async code in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # Exchange code for token
                token_data = loop.run_until_complete(
                    GitHubOAuthService.exchange_code_for_token(
                        code=code,
                        redirect_uri=redirect_uri,
                    )
                )
                access_token = token_data['access_token']
                scopes = token_data.get('scope', '').split(',')

                # Get GitHub user info
                github_user = loop.run_until_complete(
                    GitHubOAuthService.get_github_user(access_token)
                )
            finally:
                loop.close()

            # Create/link user (sync)
            user, user_created, connection_created = GitHubOAuthService.authenticate_or_create_user(
                github_user=github_user,
                access_token=access_token,
                scopes=scopes,
                source_url=source_url,
            )

            # Check if 2FA is enabled system-wide AND user has TOTP device
            is_2fa_enabled = BaseCfgModule().is_totp_enabled()
            has_device = TOTPService.has_active_device(user)

            if is_2fa_enabled and has_device:
                # Create 2FA session
                session = TwoFactorSessionService.create_session(user, request)
                logger.info(f"2FA required for OAuth user {user.email}, session {session.id}")

                return Response({
                    'requires_2fa': True,
                    'session_id': str(session.id),
                    'access': None,
                    'refresh': None,
                    'user': None,
                    'is_new_user': user_created,
                    'is_new_connection': connection_created,
                    'should_prompt_2fa': False,
                })

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'requires_2fa': False,
                'session_id': None,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'is_new_user': user_created,
                'is_new_connection': connection_created,
                'should_prompt_2fa': user.should_prompt_2fa,
            })

        except GitHubOAuthError as e:
            logger.error(f"GitHub OAuth callback error: {e}")
            return Response(
                {
                    'error': 'oauth_error',
                    'error_description': str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.exception(f"GitHub OAuth unexpected error: {e}")
            return Response(
                {
                    'error': 'server_error',
                    'error_description': 'Authentication failed',
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema(tags=['OAuth'])
class OAuthConnectionsView(APIView):
    """
    Manage user's OAuth connections.

    List all OAuth connections for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OAuthConnectionSerializer(many=True)},
        summary="List OAuth connections",
        description="Get all OAuth connections for the current user.",
    )
    def get(self, request):
        connections = OAuthConnection.objects.filter(user=request.user)
        serializer = OAuthConnectionSerializer(connections, many=True)
        return Response(serializer.data)


@extend_schema_view(
    post=extend_schema(
        tags=['OAuth'],
        request=OAuthDisconnectRequestSerializer,
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string'}}},
            400: OAuthErrorSerializer,
            404: OAuthErrorSerializer,
        },
        summary="Disconnect OAuth provider",
        description="Remove OAuth connection for the specified provider.",
    )
)
class OAuthDisconnectView(APIView):
    """
    Disconnect OAuth provider from user account.

    Removes the OAuth connection. User can still login with email/OTP.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OAuthDisconnectRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data['provider']

        # Check if connection exists
        connection = OAuthConnection.objects.filter(
            user=request.user,
            provider=provider,
        ).first()

        if not connection:
            return Response(
                {
                    'error': 'not_found',
                    'error_description': f'No {provider} connection found',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete connection
        connection.delete()

        logger.info(f"User {request.user.email} disconnected {provider}")

        return Response({
            'message': f'{provider.title()} disconnected successfully',
        })
