"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

from django.urls import path, include

urlpatterns = [
    path('health/', include('django_cfg.api.health.urls')),
    path('commands/', include('django_cfg.api.commands.urls')),
]
