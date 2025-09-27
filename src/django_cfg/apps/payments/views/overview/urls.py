"""
💰 Payments Overview Dashboard URLs

Nested router configuration for payments dashboard API endpoints.
"""
from rest_framework.routers import DefaultRouter
from .views import PaymentsDashboardViewSet

# Create router
router = DefaultRouter()

# Register payments dashboard viewset
router.register(r'dashboard', PaymentsDashboardViewSet, basename='payments-dashboard')

# URL patterns
urlpatterns = router.urls

# Available endpoints:
# GET /api/payments/overview/dashboard/overview/ - Complete payments dashboard overview
# GET /api/payments/overview/dashboard/metrics/ - Payments dashboard metrics only  
# GET /api/payments/overview/dashboard/chart_data/?period=30d - Payments chart data
# GET /api/payments/overview/dashboard/recent_payments/?limit=10 - Recent payments
# GET /api/payments/overview/dashboard/recent_transactions/?limit=10 - Recent transactions
# GET /api/payments/overview/dashboard/payment_analytics/?limit=10 - Payment analytics
# GET /api/payments/overview/dashboard/balance_overview/ - Balance overview only
# GET /api/payments/overview/dashboard/subscription_overview/ - Subscription overview only
# GET /api/payments/overview/dashboard/api_keys_overview/ - API keys overview only
