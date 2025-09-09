from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from .views import OTPViewSet
from .views.profile import UserProfileView, UserProfileUpdateView, UserProfilePartialUpdateView, upload_avatar

app_name = 'cfg_accounts'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'otp', OTPViewSet, basename='otp')

# Token-related URLs
@extend_schema(tags=['Auth'])
class CustomTokenRefreshView(TokenRefreshView):
    """Refresh JWT token."""
    pass


token_patterns = [
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]

# Profile-related URLs
profile_patterns = [
    path('', UserProfileView.as_view(), name='profile_detail'),
    path('update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('partial/', UserProfilePartialUpdateView.as_view(), name='profile_partial_update'),
    path('avatar/', upload_avatar, name='profile_avatar_upload'),
]

# Main URL patterns with nested structure
urlpatterns = [
    # ViewSet-based endpoints
    path('', include(router.urls)),
    
    # Token endpoints
    path('token/', include(token_patterns)),
    
    # Profile endpoints
    path('profile/', include(profile_patterns)),
]
