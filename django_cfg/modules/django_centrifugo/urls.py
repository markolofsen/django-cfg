"""django_centrifugo.urls — REST API URL configuration."""

from rest_framework.routers import DefaultRouter

from .views.token_api import CentrifugoTokenViewSet

router = DefaultRouter()
router.register(r"auth", CentrifugoTokenViewSet, basename="auth")

urlpatterns = router.urls
