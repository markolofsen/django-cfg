"""
Admin URLs for Universal Payment System v2.0.

Internal dashboard and management interfaces with DRF nested routing.
All URLs require staff/superuser access.
"""

from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .admin_interface.views import (
    PaymentDashboardView,
    PaymentFormView,
    PaymentDetailView,
    PaymentListView,
    AdminPaymentViewSet,
    AdminWebhookViewSet,
    AdminWebhookEventViewSet,
    WebhookTestViewSet,
    AdminStatsViewSet,
    AdminUserViewSet,
)
from .admin_interface.views.dashboard import WebhookDashboardView

app_name = 'cfg_payments_admin'

# DRF Routers for Admin API
admin_router = DefaultRouter()
admin_router.register(r'payments', AdminPaymentViewSet, basename='admin-payment')
admin_router.register(r'webhooks', AdminWebhookViewSet, basename='admin-webhook')
admin_router.register(r'stats', AdminStatsViewSet, basename='admin-stats')
admin_router.register(r'users', AdminUserViewSet, basename='admin-user')

# Nested router for webhook events
webhook_events_router = routers.NestedSimpleRouter(admin_router, r'webhooks', lookup='webhook')
webhook_events_router.register(r'events', AdminWebhookEventViewSet, basename='admin-webhook-events')

# Public API router (no authentication required)
public_router = DefaultRouter()
public_router.register(r'webhook-test', WebhookTestViewSet, basename='webhook-test')

urlpatterns = [
    # Template Views
    path('', staff_member_required(PaymentDashboardView.as_view()), name='dashboard'),
    path('dashboard/', staff_member_required(PaymentDashboardView.as_view()), name='dashboard_alt'),
    
    # Payment management templates
    path('payments/', include([
        path('', staff_member_required(PaymentListView.as_view()), name='payment-list'),
        path('create/', staff_member_required(PaymentFormView.as_view()), name='payment-form'),
        path('<uuid:pk>/', staff_member_required(PaymentDetailView.as_view()), name='payment-detail'),
    ])),
    
    # Webhook management templates
    path('webhooks/', include([
        path('', staff_member_required(WebhookDashboardView.as_view()), name='webhook-dashboard'),
        path('dashboard/', staff_member_required(WebhookDashboardView.as_view()), name='webhook-dashboard-alt'),
    ])),
    
    # API Routes with DRF ViewSets
    path('api/', include([
        path('', include(admin_router.urls)),
        path('', include(webhook_events_router.urls)),
        path('', include(public_router.urls)),  # Public API endpoints
    ])),
]
