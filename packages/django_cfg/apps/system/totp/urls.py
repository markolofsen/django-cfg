"""URL configuration for TOTP 2FA app."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BackupViewSet, DeviceViewSet, SetupViewSet, VerifyViewSet

app_name = "totp"

# Create router for viewsets
router = DefaultRouter()

# Register viewsets (but we'll use manual paths for better control)
# router.register(r'setup', SetupViewSet, basename='setup')
# router.register(r'verify', VerifyViewSet, basename='verify')
# router.register(r'devices', DeviceViewSet, basename='devices')
# router.register(r'backup', BackupViewSet, basename='backup')

# Manual URL patterns for explicit control
urlpatterns = [
    # Setup endpoints
    path(
        "setup/",
        SetupViewSet.as_view({"post": "setup"}),
        name="setup-start",
    ),
    path(
        "setup/confirm/",
        SetupViewSet.as_view({"post": "confirm"}),
        name="setup-confirm",
    ),
    # Verification endpoints
    path(
        "verify/",
        VerifyViewSet.as_view({"post": "verify"}),
        name="verify",
    ),
    path(
        "verify/backup/",
        VerifyViewSet.as_view({"post": "verify_backup"}),
        name="verify-backup",
    ),
    # Device management endpoints
    path(
        "devices/",
        DeviceViewSet.as_view({"get": "list"}),
        name="devices-list",
    ),
    path(
        "devices/<uuid:pk>/",
        DeviceViewSet.as_view({"delete": "delete_device"}),
        name="devices-delete",
    ),
    path(
        "disable/",
        DeviceViewSet.as_view({"post": "disable"}),
        name="disable",
    ),
    # Backup codes endpoints
    path(
        "backup-codes/",
        BackupViewSet.as_view({"get": "status"}),
        name="backup-status",
    ),
    path(
        "backup-codes/regenerate/",
        BackupViewSet.as_view({"post": "regenerate"}),
        name="backup-regenerate",
    ),
]

# Add router URLs if needed
# urlpatterns += router.urls




