"""
Database Backup URL Configuration.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api.views import BackupViewSet, RestoreViewSet

router = DefaultRouter()
router.register(r"backups", BackupViewSet, basename="backup")
router.register(r"restores", RestoreViewSet, basename="restore")

app_name = "db_backup"

urlpatterns = [
    path("", include(router.urls)),
]
