"""URL configuration for the Payments app.

Mounted at ``cfg/payments/`` by django-cfg's URL wiring when
``PaymentsConfig.enabled`` is on. Specific patterns (webhook, checkout) come
BEFORE the generic router routes.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from django_cfg.apps.payments.api import (
    CheckoutCreateView,
    PaymentViewSet,
    StripeWebhookView,
)

app_name = "cfg_payments"

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = [
    # Webhook is signature-authed + CSRF-exempt; excluded from the OpenAPI client.
    path("webhook/stripe/", StripeWebhookView.as_view(), name="webhook-stripe"),
    path("checkout/", CheckoutCreateView.as_view(), name="checkout"),
    path("", include(router.urls)),
]
