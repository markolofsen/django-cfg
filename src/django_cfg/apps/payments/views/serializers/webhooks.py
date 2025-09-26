"""
Webhook serializers for the Universal Payment System v2.0.

DRF serializers for webhook endpoints and data validation.
"""

from rest_framework import serializers
from django_cfg.modules.django_logger import get_logger

logger = get_logger(__name__)


class WebhookSerializer(serializers.Serializer):
    """
    Generic webhook serializer.
    
    Base serializer for all webhook types.
    """
    
    provider = serializers.CharField(max_length=50, help_text="Payment provider name")
    success = serializers.BooleanField(help_text="Processing success status")
    message = serializers.CharField(max_length=500, help_text="Processing message")
    
    class Meta:
        fields = ['provider', 'success', 'message']


class WebhookDataSerializer(serializers.Serializer):
    """
    Serializer for incoming webhook data.
    
    Generic webhook data structure for all providers.
    """
    
    provider = serializers.CharField(max_length=50, help_text="Payment provider name")
    payment_id = serializers.CharField(max_length=256, help_text="Provider payment ID")
    status = serializers.CharField(max_length=50, help_text="Payment status")
    amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False, help_text="Payment amount")
    currency = serializers.CharField(max_length=10, required=False, help_text="Payment currency")
    transaction_hash = serializers.CharField(max_length=256, required=False, help_text="Blockchain transaction hash")
    confirmations = serializers.IntegerField(required=False, help_text="Number of confirmations")
    
    # Raw webhook data
    raw_data = serializers.JSONField(help_text="Raw webhook payload")
    
    class Meta:
        fields = [
            'provider', 'payment_id', 'status', 'amount', 
            'currency', 'transaction_hash', 'confirmations', 'raw_data'
        ]


class WebhookResponseSerializer(serializers.Serializer):
    """
    Serializer for webhook processing response.
    
    Standard response format for all webhook endpoints.
    """
    
    success = serializers.BooleanField(help_text="Whether webhook was processed successfully")
    message = serializers.CharField(max_length=500, help_text="Processing result message")
    payment_id = serializers.CharField(max_length=256, required=False, help_text="Internal payment ID")
    provider_payment_id = serializers.CharField(max_length=256, required=False, help_text="Provider payment ID")
    processed_at = serializers.DateTimeField(required=False, help_text="Processing timestamp")
    
    class Meta:
        fields = ['success', 'message', 'payment_id', 'provider_payment_id', 'processed_at']


class WebhookHealthSerializer(serializers.Serializer):
    """
    Serializer for webhook health check response.
    """
    
    status = serializers.CharField(max_length=20, help_text="Health status")
    timestamp = serializers.DateTimeField(help_text="Check timestamp")
    providers = serializers.JSONField(help_text="Provider health status")
    
    class Meta:
        fields = ['status', 'timestamp', 'providers']


class WebhookStatsSerializer(serializers.Serializer):
    """
    Serializer for webhook statistics response.
    """
    
    total_webhooks = serializers.IntegerField(help_text="Total webhooks processed")
    successful_webhooks = serializers.IntegerField(help_text="Successfully processed webhooks")
    failed_webhooks = serializers.IntegerField(help_text="Failed webhook processing attempts")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    providers = serializers.JSONField(help_text="Per-provider statistics")
    
    class Meta:
        fields = ['total_webhooks', 'successful_webhooks', 'failed_webhooks', 'success_rate', 'providers']


class SupportedProvidersSerializer(serializers.Serializer):
    """
    Serializer for supported providers response.
    """
    
    success = serializers.BooleanField(help_text="Request success status")
    providers = serializers.JSONField(help_text="List of supported providers")
    total_count = serializers.IntegerField(help_text="Total number of providers")
    timestamp = serializers.DateTimeField(help_text="Response timestamp")
    
    class Meta:
        fields = ['success', 'providers', 'total_count', 'timestamp']


class NowPaymentsWebhookSerializer(serializers.Serializer):
    """
    Serializer for NowPayments webhook data.
    
    Specific to NowPayments IPN format.
    """
    
    payment_id = serializers.CharField(max_length=256, help_text="NowPayments payment ID")
    payment_status = serializers.CharField(max_length=50, help_text="Payment status")
    pay_address = serializers.CharField(max_length=256, required=False, help_text="Payment address")
    price_amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False, help_text="Price amount")
    price_currency = serializers.CharField(max_length=10, required=False, help_text="Price currency")
    pay_amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False, help_text="Pay amount")
    pay_currency = serializers.CharField(max_length=10, required=False, help_text="Pay currency")
    order_id = serializers.CharField(max_length=256, required=False, help_text="Order ID")
    order_description = serializers.CharField(max_length=500, required=False, help_text="Order description")
    purchase_id = serializers.CharField(max_length=256, required=False, help_text="Purchase ID")
    outcome_amount = serializers.DecimalField(max_digits=20, decimal_places=8, required=False, help_text="Outcome amount")
    outcome_currency = serializers.CharField(max_length=10, required=False, help_text="Outcome currency")
    
    class Meta:
        fields = [
            'payment_id', 'payment_status', 'pay_address', 'price_amount', 'price_currency',
            'pay_amount', 'pay_currency', 'order_id', 'order_description', 'purchase_id',
            'outcome_amount', 'outcome_currency'
        ]
