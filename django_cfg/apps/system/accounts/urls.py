from django.urls import include, path
from drf_spectacular.utils import extend_schema
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import OTPViewSet
from .views.oauth import (
    GitHubAuthorizeView,
    GitHubCallbackView,
    OAuthConnectionsView,
    OAuthDisconnectView,
    OAuthProvidersView,
)
from .views.api_key import APIKeyViewSet
from .views.profile import (
    AccountDeleteView,
    UserProfilePartialUpdateView,
    UserProfileUpdateView,
    UserProfileView,
    upload_avatar,
)

app_name = 'cfg_accounts'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'otp', OTPViewSet, basename='otp')

# Token-related URLs
@extend_schema(tags=["cfg_accounts_auth"])
class CustomTokenRefreshView(TokenRefreshView):
    """Refresh JWT token.

    DPoP-aware: when the incoming refresh token is key-bound (`cnf.jkt`), the
    rotated access/refresh in the response are re-stamped with the same `cnf`
    (stock SimpleJWT drops it from the derived access), and a matching DPoP
    proof is required on the refresh request — so a stolen refresh token can't
    be used to mint fresh tokens.
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        try:
            from rest_framework import status as drf_status
            from rest_framework_simplejwt.tokens import RefreshToken
            from django_cfg.middleware.dpop import (
                DPoPError,
                is_dpop_enabled,
                rebind_refresh_response,
            )

            if (
                is_dpop_enabled()
                and response.status_code == 200
                and isinstance(response.data, dict)
            ):
                incoming = request.data.get("refresh")
                cnf = RefreshToken(incoming).get("cnf") if incoming else None
                if cnf:
                    rebind_refresh_response(response.data, cnf, request)
                    response._is_rendered = False
                    response.render()
        except DPoPError:
            from rest_framework.response import Response
            from rest_framework import status as drf_status
            return Response(
                {"detail": "Invalid DPoP proof for token refresh."},
                status=drf_status.HTTP_401_UNAUTHORIZED,
            )
        except Exception:
            # Never break refresh on an unexpected rebind error — fall back to
            # the stock (unbound) response rather than 500.
            pass
        return response


token_patterns = [
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]

# Profile-related URLs
profile_patterns = [
    path('', UserProfileView.as_view(), name='profile_detail'),
    path('update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('partial/', UserProfilePartialUpdateView.as_view(), name='profile_partial_update'),
    path('avatar/', upload_avatar, name='profile_avatar_upload'),
    path('delete/', AccountDeleteView.as_view(), name='account_delete'),
]

# API key-related URLs
api_key_patterns = [
    path('', APIKeyViewSet.as_view({'get': 'retrieve_key'}), name='api_key_detail'),
    path('regenerate/', APIKeyViewSet.as_view({'post': 'regenerate'}), name='api_key_regenerate'),
    path('test/', APIKeyViewSet.as_view({'post': 'test_key'}), name='api_key_test'),
]

# OAuth-related URLs
oauth_patterns = [
    path('providers/', OAuthProvidersView.as_view(), name='oauth_providers'),
    path('github/authorize/', GitHubAuthorizeView.as_view(), name='github_authorize'),
    path('github/callback/', GitHubCallbackView.as_view(), name='github_callback'),
    path('connections/', OAuthConnectionsView.as_view(), name='oauth_connections'),
    path('disconnect/', OAuthDisconnectView.as_view(), name='oauth_disconnect'),
]

# Main URL patterns with nested structure
urlpatterns = [
    # ViewSet-based endpoints
    path('', include(router.urls)),

    # Token endpoints
    path('token/', include(token_patterns)),

    # Profile endpoints
    path('profile/', include(profile_patterns)),

    # API key endpoints
    path('api-key/', include(api_key_patterns)),

    # OAuth endpoints
    path('oauth/', include(oauth_patterns)),
]
