"""
Admin URLs for Universal Payment System v2.0.

Internal dashboard and management interfaces.
All URLs require staff/superuser access.
"""

from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required

from .admin_interface.views import (
    WebhookDashboardView,
    PaymentFormView,
    PaymentStatusView,
    PaymentListView,
    PaymentDashboardView,
    CurrencyConverterView,
)

app_name = 'cfg_payments_admin'

urlpatterns = [
    # Main dashboard
    path('', staff_member_required(PaymentDashboardView.as_view()), name='dashboard'),
    path('dashboard/', staff_member_required(PaymentDashboardView.as_view()), name='dashboard_alt'),
    
    # Payment management
    path('payments/', include([
        path('', staff_member_required(PaymentListView.as_view()), name='payment-list'),
        path('create/', staff_member_required(PaymentFormView.as_view()), name='payment-create'),
        path('<uuid:pk>/', staff_member_required(PaymentStatusView.as_view()), name='payment-detail'),
        path('status/<uuid:pk>/', staff_member_required(PaymentStatusView.as_view()), name='payment-status'),
    ])),
    
    # Webhook management
    path('webhooks/', include([
        path('', staff_member_required(WebhookDashboardView.as_view()), name='webhook-dashboard'),
        path('dashboard/', staff_member_required(WebhookDashboardView.as_view()), name='webhook-dashboard-alt'),
    ])),
    
    # Tools and utilities
    path('tools/', include([
        path('converter/', staff_member_required(CurrencyConverterView.as_view()), name='currency-converter'),
    ])),
    
    # Development/testing tools (only in DEBUG mode)
    # path('test/', PaymentTestView.as_view(), name='test'),
    # path('debug/', PaymentDebugView.as_view(), name='debug'),
]
