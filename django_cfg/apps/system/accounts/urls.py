from django.urls import include, path
from drf_spectacular.utils import extend_schema
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import OTPViewSet, PasswordLoginView
from .views.oauth import (
    PROVIDER_VIEWS,
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

    Stock SimpleJWT refresh. A ``cnf`` claim left in a token issued by an
    older release is ignored: the token refreshes like any other.
    """


@extend_schema(tags=["cfg_accounts_auth"])
class CustomTokenBlacklistView(TokenBlacklistView):
    """Revoke a refresh token (logout).

    Blacklists the posted refresh token so it can never mint another access
    token. Called best-effort by the client's logout — without it, "logout"
    is purely client-side and a stolen refresh token survives until expiry.
    """


token_patterns = [
    # Password grant.
    path('', PasswordLoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('blacklist/', CustomTokenBlacklistView.as_view(), name='token_blacklist'),
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
    path('reveal/', APIKeyViewSet.as_view({'post': 'reveal'}), name='api_key_reveal'),
    path('regenerate/', APIKeyViewSet.as_view({'post': 'regenerate'}), name='api_key_regenerate'),
    path('test/', APIKeyViewSet.as_view({'post': 'test_key'}), name='api_key_test'),
]

# OAuth-related URLs. One literal path pair per provider in the registry
# (oauth/github/*, oauth/google/*): a single oauth/<provider>/ route would
# change GitHub's generated operation ids.
oauth_patterns = [
    path('providers/', OAuthProvidersView.as_view(), name='oauth_providers'),
    *[
        route
        for provider_id, (authorize_view, callback_view) in PROVIDER_VIEWS.items()
        for route in (
            path(f'{provider_id}/authorize/', authorize_view.as_view(), name=f'{provider_id}_authorize'),
            path(f'{provider_id}/callback/', callback_view.as_view(), name=f'{provider_id}_callback'),
        )
    ],
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
