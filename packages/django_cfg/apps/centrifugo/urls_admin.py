"""
Admin URLs for Centrifugo dashboard.

Dashboard interface for monitoring Centrifugo publish activity.
"""

from django.urls import include, path

from .views import dashboard_view

app_name = 'django_cfg_centrifugo_admin'


urlpatterns = [
    # Dashboard page
    path('', dashboard_view, name='dashboard'),

    # Include API endpoints for dashboard AJAX calls
    path('api/', include('django_cfg.apps.centrifugo.urls')),
]
