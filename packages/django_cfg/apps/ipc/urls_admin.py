"""
Admin URLs for IPC/RPC dashboard.

Dashboard interface for monitoring RPC activity.
"""

from django.urls import include, path

from .views import dashboard_view

app_name = 'django_cfg_ipc_admin'


urlpatterns = [
    # Dashboard page
    path('', dashboard_view, name='dashboard'),

    # Include API endpoints for dashboard AJAX calls
    path('api/', include('django_cfg.apps.ipc.urls')),
]
