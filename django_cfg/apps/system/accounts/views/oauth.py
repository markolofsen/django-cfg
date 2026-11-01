"""
OAuth Views

One authorize/callback pair per provider, built from the provider registry
(``make_views``), so GitHub and Google share every line of the flow. URLs stay
literal per provider (``oauth/github/*``, ``oauth/google/*``) to keep generated
operation ids stable.
"""

import logging
from typing import Dict, Tuple, Type

from django.db import transaction
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
from ..services.oauth import (
    OAuthError,
    OAuthErrorCode,
    OAuthService,
    all_providers,
    enabled_providers,
    finalize_login,
    get_provider,
)
from ..services.oauth.redirect import resolve_redirect_uri

logger = logging.getLogger(__name__)


def error_response(code: OAuthErrorCode, description: str = "", status_code: int = 0) -> Response:
    """The wire shape of every OAuth failure: ``{error, error_description}``."""
    error = OAuthError(code, description or None)
    return Response(
        {"error": error.code.value, "error_description": error.description},
        status=status_code or error.status,
    )


@extend_schema(tags=["cfg_accounts_oauth"])
class OAuthProvidersView(APIView):
    """List the sign-in providers that are configured."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        responses={200: OAuthProvidersResponseSerializer},
        summary="List OAuth providers",
        description="Providers that are configured, in display order. The login screen shows exactly these buttons.",
    )
    def get(self, request):  # noqa: ARG002
        return Response({
            "providers": [{"id": p.id, "name": p.name, "icon": p.icon} for p in enabled_providers()],
        })


# The flow runs outside the request transaction: the state must be spent for
# good the moment it is read (a rollback would un-spend it), and no transaction
# should stay open across calls to the provider.
@method_decorator(transaction.non_atomic_requests, name="dispatch")
class OAuthAuthorizeView(APIView):
    """Start the flow for ``provider_id``: returns the authorization URL and the state."""

    permission_classes = [AllowAny]
    authentication_classes = []
    provider_id = ""

    def post(self, request):
        provider = get_provider(self.provider_id)
        if not provider.is_enabled():
            return error_response(provider.disabled_code)
        if getattr(request, "limited", False):
            return error_response(OAuthErrorCode.RATE_LIMITED)

        serializer = OAuthAuthorizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            redirect_uri = resolve_redirect_uri(
                request, provider.id, serializer.validated_data.get("redirect_uri", "")
            )
            authorization_url, state = OAuthService.start(
                provider,
                redirect_uri=redirect_uri,
                source_url=serializer.validated_data.get("source_url", ""),
            )
        except OAuthError as exc:
            logger.warning("OAuth %s authorize refused: %s", provider.id, exc.code.value)
            return error_response(exc.code, exc.description)
        except Exception:
            logger.exception("OAuth %s authorize failed", provider.id)
            return error_response(OAuthErrorCode.SERVER_ERROR)

        return Response({"authorization_url": authorization_url, "state": state})


@method_decorator(transaction.non_atomic_requests, name="dispatch")
class OAuthCallbackView(APIView):
    """Finish the flow for ``provider_id``: consume the state, exchange the code, sign the user in."""

    permission_classes = [AllowAny]
    authentication_classes = []
    provider_id = ""

    def post(self, request):
        provider = get_provider(self.provider_id)
        if not provider.is_enabled():
            return error_response(provider.disabled_code)
        if getattr(request, "limited", False):
            return error_response(OAuthErrorCode.RATE_LIMITED)

        serializer = OAuthCallbackRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(OAuthErrorCode.INVALID_STATE)

        try:
            result = OAuthService.complete(
                provider,
                code=serializer.validated_data["code"],
                state=serializer.validated_data["state"],
            )
            body = finalize_login(request, result, sender=type(self))
        except OAuthError as exc:
            logger.warning("OAuth %s callback refused: %s", provider.id, exc.code.value)
            return error_response(exc.code, exc.description)
        except Exception:
            logger.exception("OAuth %s callback failed", provider.id)
            return error_response(OAuthErrorCode.SERVER_ERROR)

        return Response(body)


def make_views(provider) -> Tuple[Type[APIView], Type[APIView]]:
    """The authorize and callback view classes of one provider, documented for OpenAPI."""
    authorize = type(
        f"{provider.name}AuthorizeView",
        (OAuthAuthorizeView,),
        {"provider_id": provider.id, "__doc__": f"Start {provider.name} sign-in."},
    )
    callback = type(
        f"{provider.name}CallbackView",
        (OAuthCallbackView,),
        {"provider_id": provider.id, "__doc__": f"Complete {provider.name} sign-in."},
    )
    authorize = method_decorator(ratelimit(key="ip", rate="20/m", block=False), name="post")(authorize)
    callback = method_decorator(ratelimit(key="ip", rate="10/m", block=False), name="post")(callback)
    authorize = extend_schema_view(
        post=extend_schema(
            tags=["cfg_accounts_oauth"],
            request=OAuthAuthorizeRequestSerializer,
            responses={200: OAuthAuthorizeResponseSerializer, 400: OAuthErrorSerializer, 503: OAuthErrorSerializer},
            summary=f"Start {provider.name} OAuth",
            description=(
                f"Generate the {provider.name} authorization URL. Redirect the user to it to start "
                "authentication. The redirect URI is derived from the request Origin."
            ),
        )
    )(authorize)
    callback = extend_schema_view(
        post=extend_schema(
            tags=["cfg_accounts_oauth"],
            request=OAuthCallbackRequestSerializer,
            responses={
                200: OAuthTokenResponseSerializer,
                400: OAuthErrorSerializer,
                403: OAuthErrorSerializer,
                429: OAuthErrorSerializer,
                502: OAuthErrorSerializer,
                503: OAuthErrorSerializer,
            },
            summary=f"Complete {provider.name} OAuth",
            description=(
                f"Exchange the authorization code for JWT tokens. Call this after {provider.name} "
                "redirects back with a code. The state is single use."
            ),
        )
    )(callback)
    return authorize, callback


PROVIDER_VIEWS: Dict[str, Tuple[Type[APIView], Type[APIView]]] = {
    provider.id: make_views(provider) for provider in all_providers()
}


@extend_schema(tags=["cfg_accounts_oauth"])
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
        tags=["cfg_accounts_oauth"],
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
                    'error': OAuthErrorCode.NOT_FOUND.value,
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
