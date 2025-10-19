"""
Lead URLs - API routing for the leads application.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet

# Create router
# Note: Empty prefix because URL is already under cfg/leads/
router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

app_name = "cfg_leads"

urlpatterns = [
    path("", include(router.urls)),
]
