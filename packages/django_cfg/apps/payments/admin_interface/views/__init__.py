"""
Admin Interface Views for Universal Payment System v2.0.

DRF ViewSets and template views for admin dashboard and management interfaces.
"""

# Template Views
from .dashboard import PaymentDashboardView, WebhookDashboardView
from .forms import PaymentFormView, PaymentDetailView, PaymentListView

# API ViewSets
from .api import (
    AdminPaymentViewSet,
    AdminWebhookViewSet,
    AdminWebhookEventViewSet,
    WebhookTestViewSet,
    AdminStatsViewSet,
    AdminUserViewSet,
)

__all__ = [
    # Template Views
    'PaymentDashboardView',
    'WebhookDashboardView',
    'PaymentFormView', 
    'PaymentDetailView',
    'PaymentListView',
    
    # API ViewSets
    'AdminPaymentViewSet',
    'AdminWebhookViewSet',
    'AdminWebhookEventViewSet',
    'WebhookTestViewSet',
    'AdminStatsViewSet',
    'AdminUserViewSet',
]