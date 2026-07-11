"""DRF views for the Payments app.

Three surfaces:
- ``PaymentViewSet`` — authed, owner-scoped list/retrieve of the caller's payments.
- ``CheckoutCreateView`` — authed; creates a Payment + provider checkout for the
  resolved owner.
- ``StripeWebhookView`` — UNauthenticated by JWT, CSRF-exempt, signature-verified
  on the RAW body. Persists the event fast, defers fulfillment to RQ, returns 200.
"""

from __future__ import annotations

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from django_cfg.apps.payments.api.owner import resolve_owner
from django_cfg.apps.payments.api.serializers import (
    CheckoutCreateRequestSerializer,
    CheckoutCreateResponseSerializer,
    PaymentSerializer,
)
from django_cfg.apps.payments.config import get_payments_config
from django_cfg.apps.payments.models import Payment
from django_cfg.apps.payments.providers import get_provider  # webhook view
from django_cfg.apps.payments.providers.base import ProviderWebhookError
from django_cfg.apps.payments.services import PaymentError, PaymentService

logger = logging.getLogger(__name__)


@extend_schema(tags=["Payments"])
@extend_schema_view(
    list=extend_schema(summary="List payments", responses={200: PaymentSerializer(many=True)}),
    retrieve=extend_schema(summary="Retrieve a payment", responses={200: PaymentSerializer}),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Payments for the caller's resolved owner (see ``api.owner``)."""

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "short_id"
    queryset = Payment.objects.none()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()
        owner = resolve_owner(self.request)
        return Payment.objects.filter(owner=owner)


@extend_schema(tags=["Payments"])
class CheckoutCreateView(APIView):
    """Create a checkout (PaymentIntent) for the caller's owner."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Create checkout",
        request=CheckoutCreateRequestSerializer,
        responses={200: CheckoutCreateResponseSerializer},
    )
    def post(self, request):
        serializer = CheckoutCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        owner = resolve_owner(request)

        # Idempotency: an explicit client key wins; else one checkout per
        # (owner, reference, provider) re-uses the same key, so a double-click
        # returns the existing Payment instead of charging twice. Without a
        # reference the service mints a random key (no cross-request dedupe).
        idempotency_key = data["idempotency_key"] or None
        if idempotency_key is None and data["reference_id"]:
            idempotency_key = (
                f"checkout-{owner.pk}-{data['reference_kind']}-"
                f"{data['reference_id']}-{data['provider']}"
            )

        try:
            payment, session = PaymentService.create_checkout(
                owner=owner,
                amount=data["amount"],
                currency=data["currency"],
                reference_kind=data["reference_kind"],
                reference_id=data["reference_id"],
                created_by=request.user,
                idempotency_key=idempotency_key,
                provider_name=data["provider"],
            )
        except PaymentError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        body = {
            "payment_short_id": payment.short_id,
            "provider": payment.provider,
            "status": payment.status,
            "amount": payment.amount,
            "currency": payment.currency,
            "client_secret": session.client_secret,
            "redirect_url": session.redirect_url,
            "publishable_key": get_payments_config().stripe_publishable_key or None,
        }
        return Response(CheckoutCreateResponseSerializer(body).data)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """Stripe webhook receiver.

    Unauthenticated by JWT (authenticated by signature instead), CSRF-exempt,
    no DRF body parsing (reads the raw bytes for HMAC). Persists + defers, then
    returns 200 fast.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes: list = []
    parser_classes: list = []  # do NOT let DRF consume/reparse the raw body

    # Keep this endpoint out of the generated OpenAPI client (external callers).
    @extend_schema(exclude=True)
    def post(self, request):
        provider_name = "stripe"
        payload: bytes = request.body
        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        provider = get_provider(provider_name)
        try:
            result = provider.verify_and_parse_webhook(
                payload=payload, signature=signature,
            )
        except ProviderWebhookError as exc:
            logger.warning("stripe webhook rejected: %s", exc)
            return Response({"detail": "Invalid signature."}, status=400)

        # Defer fulfillment to RQ; fall back to synchronous if Redis is absent.
        try:
            import django_rq

            queue = django_rq.get_queue("default")
            queue.enqueue(
                "django_cfg.apps.payments.tasks.process_webhook_event",
                provider_name,
                result.event_id,
                result.event_type,
                result.external_id,
                result.amount,
                result.currency,
                result.raw,
            )
        except Exception as exc:  # noqa: BLE001 — dev/no-redis fallback
            logger.warning("RQ enqueue failed (%s); handling webhook inline.", exc)
            PaymentService.handle_webhook(result=result, provider_name=provider_name)

        return Response({"received": True}, status=200)
