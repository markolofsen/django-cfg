"""
URL patterns for RPC Dashboard.

Mount at: /admin/rpc/ or custom path
"""

from django.urls import path
from . import views

app_name = 'django_ipc_dashboard'

urlpatterns = [
    # Main dashboard page
    path('', views.dashboard_view, name='dashboard'),

    # API endpoints
    path('api/overview/', views.api_overview_stats, name='api_overview'),
    path('api/requests/', views.api_recent_requests, name='api_requests'),
    path('api/notifications/', views.api_notification_stats, name='api_notifications'),
    path('api/methods/', views.api_method_stats, name='api_methods'),
    path('api/health/', views.api_health_check, name='api_health'),
]
