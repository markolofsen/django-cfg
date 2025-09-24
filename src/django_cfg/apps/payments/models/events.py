"""
Event sourcing models for the universal payments system.
"""

from django.db import models
from .base import UUIDTimestampedModel


class PaymentEvent(UUIDTimestampedModel):
    """Event sourcing for payment operations - immutable audit trail."""
    
    class EventType(models.TextChoices):
        PAYMENT_CREATED = 'payment_created', 'Payment Created'
        WEBHOOK_RECEIVED = 'webhook_received', 'Webhook Received'
        WEBHOOK_PROCESSED = 'webhook_processed', 'Webhook Processed'
        BALANCE_UPDATED = 'balance_updated', 'Balance Updated'
        REFUND_PROCESSED = 'refund_processed', 'Refund Processed'
        STATUS_CHANGED = 'status_changed', 'Status Changed'
        ERROR_OCCURRED = 'error_occurred', 'Error Occurred'
    
    # Event identification
    payment_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Payment identifier"
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices,
        db_index=True,
        help_text="Type of event"
    )
    sequence_number = models.PositiveBigIntegerField(
        help_text="Sequential number per payment"
    )
    
    # Event data (JSON for flexibility)
    event_data = models.JSONField(
        help_text="Event data payload"
    )
    
    # Operational metadata
    processed_by = models.CharField(
        max_length=100,
        help_text="Worker/server that processed this event"
    )
    correlation_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Correlation ID for tracing"
    )
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="Idempotency key to prevent duplicates"
    )
    
    class Meta:
        db_table = 'payment_events'
        verbose_name = "Payment Event"
        verbose_name_plural = "Payment Events"
        indexes = [
            models.Index(fields=['payment_id', 'sequence_number']),
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['idempotency_key']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['sequence_number']
    
    def __str__(self):
        return f"Event {self.sequence_number}: {self.event_type} for {self.payment_id}"
