"""
Withdrawal admin actions.

Standalone action handlers for Withdrawal admin.
"""
from django.utils import timezone

from django_cfg.modules.django_logging import get_logger

logger = get_logger("withdrawal_actions")


def approve_withdrawals(modeladmin, request, queryset):
    """Approve selected withdrawal requests."""
    updated = queryset.filter(status='pending').update(
        status='approved',
        admin_user=request.user,
        approved_at=timezone.now(),
        status_changed_at=timezone.now()
    )

    modeladmin.message_user(
        request,
        f"Successfully approved {updated} withdrawal(s).",
        level='SUCCESS'
    )
    logger.info(f"Admin {request.user.username} approved {updated} withdrawal requests")


def reject_withdrawals(modeladmin, request, queryset):
    """Reject selected withdrawal requests."""
    updated = queryset.filter(status='pending').update(
        status='rejected',
        admin_user=request.user,
        admin_notes="Rejected via bulk action",
        rejected_at=timezone.now(),
        status_changed_at=timezone.now()
    )

    modeladmin.message_user(
        request,
        f"Successfully rejected {updated} withdrawal(s).",
        level='WARNING'
    )
    logger.warning(f"Admin {request.user.username} rejected {updated} withdrawal requests")


def mark_as_completed(modeladmin, request, queryset):
    """Mark approved/processing withdrawals as completed."""
    updated = queryset.filter(status__in=['approved', 'processing']).update(
        status='completed',
        completed_at=timezone.now(),
        status_changed_at=timezone.now()
    )

    modeladmin.message_user(
        request,
        f"Successfully marked {updated} withdrawal(s) as completed.",
        level='SUCCESS'
    )
    logger.info(f"Admin {request.user.username} marked {updated} withdrawals as completed")
