"""
Template URLs for Payment Dashboard.

All URLs require superuser access as this is an internal admin tool.
"""

from django.urls import path
from .views.templates import (
    PaymentDashboardView,
    PaymentDetailView,
    PaymentCreateView,
    PaymentStatsView,
    PaymentListView,
    PaymentQRCodeView,
    PaymentTestView,
    payment_status_ajax,
    payment_events_ajax,
)
from .views.templates.ajax import (
    payment_stats_ajax,
    payment_search_ajax,
    payment_action_ajax,
    provider_currencies_ajax,
    all_providers_data_ajax,
)
from .views.templates.qr_code import qr_code_data_ajax

app_name = 'payments_dashboard'

urlpatterns = [
    # Main dashboard
    path('', PaymentDashboardView.as_view(), name='dashboard'),
    path('dashboard/', PaymentDashboardView.as_view(), name='dashboard_alt'),
    
    # Payment management
    path('list/', PaymentListView.as_view(), name='list'),
    path('create/', PaymentCreateView.as_view(), name='create'),
    path('stats/', PaymentStatsView.as_view(), name='stats'),
    
    # Payment details
    path('payment/<uuid:pk>/', PaymentDetailView.as_view(), name='detail'),
    path('payment/<uuid:pk>/qr/', PaymentQRCodeView.as_view(), name='qr_code'),
    
    # AJAX endpoints
    path('ajax/payment/<uuid:payment_id>/status/', payment_status_ajax, name='payment_status_ajax'),
    path('ajax/payment/<uuid:payment_id>/events/', payment_events_ajax, name='payment_events_ajax'),
    path('ajax/payment/<uuid:payment_id>/qr-data/', qr_code_data_ajax, name='qr_data_ajax'),
    path('ajax/payment/<uuid:payment_id>/action/', payment_action_ajax, name='payment_action_ajax'),
    path('ajax/stats/', payment_stats_ajax, name='payment_stats_ajax'),
    path('ajax/search/', payment_search_ajax, name='payment_search_ajax'),
    
    # Provider and Currency AJAX endpoints
    path('ajax/provider/currencies/', provider_currencies_ajax, name='provider_currencies_ajax'),
    path('ajax/providers/all/', all_providers_data_ajax, name='all_providers_data_ajax'),
    
    # Development/testing
    path('test/', PaymentTestView.as_view(), name='test'),
]
