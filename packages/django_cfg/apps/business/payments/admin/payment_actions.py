"""
Payment admin actions.

Standalone action handlers for Payment admin.
"""

from django_cfg.modules.django_logging import get_logger

from ..models import Payment

logger = get_logger("payment_admin")


def mark_as_completed(modeladmin, request, queryset):
    """Mark selected payments as completed."""
    updated = 0
    for payment in queryset.filter(status__in=['pending', 'confirming', 'confirmed']):
        success = Payment.objects.update_payment_status(
            payment,
            'completed'
        )
        if success:
            updated += 1

    modeladmin.message_user(
        request,
        f"Successfully marked {updated} payment(s) as completed.",
        level='SUCCESS'
    )


def mark_as_failed(modeladmin, request, queryset):
    """Mark selected payments as failed."""
    updated = 0
    for payment in queryset.filter(status__in=['pending', 'confirming', 'confirmed']):
        success = Payment.objects.update_payment_status(
            payment,
            'failed'
        )
        if success:
            updated += 1

    modeladmin.message_user(
        request,
        f"Successfully marked {updated} payment(s) as failed.",
        level='WARNING'
    )


def cancel_payments(modeladmin, request, queryset):
    """Cancel selected payments."""
    updated = 0
    for payment in queryset.filter(status__in=['pending', 'confirming']):
        success = Payment.objects.update_payment_status(
            payment,
            'cancelled'
        )
        if success:
            updated += 1

    modeladmin.message_user(
        request,
        f"Successfully cancelled {updated} payment(s).",
        level='WARNING'
    )
