"""
Lead URLs - API routing for the leads application.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LeadViewSet

# Create router
router = DefaultRouter()
router.register(r"leads", LeadViewSet, basename="lead")

app_name = "cfg_leads"

urlpatterns = [
    path("", include(router.urls)),
]