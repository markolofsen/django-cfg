"""DRF serializers for the Payments API (→ generated clients)."""

from __future__ import annotations

from rest_framework import serializers

from django_cfg.apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "short_id",
            "owner",
            "reference_kind",
            "reference_id",
            "provider",
            "status",
            "amount",
            "currency",
            "amount_refunded",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CheckoutCreateRequestSerializer(serializers.Serializer):
    """Request body for creating a checkout.

    ``amount`` is integer MINOR units (cents). The generic engine accepts it
    from the request — hosts whose amounts must come from a frozen server-side
    source (an order, a plan) should subclass ``CheckoutCreateView`` and derive
    the amount there instead of exposing this field to clients.
    """

    amount = serializers.IntegerField(min_value=1)
    currency = serializers.CharField(max_length=8, required=False, allow_null=True, default=None)
    reference_kind = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    reference_id = serializers.CharField(max_length=64, required=False, allow_blank=True, default="")
    provider = serializers.CharField(max_length=32, required=False, default="stripe")
    # Optional client-supplied dedupe key; when omitted and a reference is
    # given, the view derives a deterministic key from (owner, reference).
    idempotency_key = serializers.CharField(max_length=128, required=False, allow_blank=True, default="")


class CheckoutCreateResponseSerializer(serializers.Serializer):
    payment_short_id = serializers.CharField()
    provider = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.IntegerField()
    currency = serializers.CharField()
    client_secret = serializers.CharField(allow_null=True)
    redirect_url = serializers.CharField(allow_null=True)
    publishable_key = serializers.CharField(allow_null=True)
