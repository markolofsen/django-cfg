"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

from django.urls import path, include

urlpatterns = [
    path('health/', include('django_cfg.apps.api.health.urls')),
    path('commands/', include('django_cfg.apps.api.commands.urls')),
    path('support/', include('django_cfg.apps.support.urls')),
    path('accounts/', include('django_cfg.apps.accounts.urls')),
]
