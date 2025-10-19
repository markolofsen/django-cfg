"""
Toolsets admin actions.

Standalone action handlers for Tool Execution, Approval Log, and Toolset Configuration admins.
"""

from datetime import timedelta

from django.utils import timezone

from django_cfg.modules.django_logging import get_logger

logger = get_logger("toolsets_admin")


# ===== Tool Execution Actions =====

def retry_failed_executions(modeladmin, request, queryset):
    """Retry failed tool executions."""
    failed_count = queryset.filter(status='failed').count()
    modeladmin.message_user(
        request,
        f"Retry functionality not implemented yet. {failed_count} failed executions selected.",
        level='WARNING'
    )


def clear_errors(modeladmin, request, queryset):
    """Clear error messages from executions."""
    updated = queryset.update(error_message=None)
    modeladmin.message_user(
        request,
        f"Cleared error messages from {updated} executions.",
        level='INFO'
    )


# ===== Approval Log Actions =====

def approve_pending(modeladmin, request, queryset):
    """Approve pending approvals."""
    updated = queryset.filter(status='pending').update(
        status='approved',
        approved_by=request.user,
        decision_time=timezone.now()
    )
    modeladmin.message_user(
        request,
        f"Approved {updated} pending requests.",
        level='SUCCESS'
    )


def reject_pending(modeladmin, request, queryset):
    """Reject pending approvals."""
    updated = queryset.filter(status='pending').update(
        status='rejected',
        approved_by=request.user,
        decision_time=timezone.now()
    )
    modeladmin.message_user(
        request,
        f"Rejected {updated} pending requests.",
        level='WARNING'
    )


def extend_expiry(modeladmin, request, queryset):
    """Extend expiry time for pending approvals."""
    new_expiry = timezone.now() + timedelta(hours=24)
    updated = queryset.filter(status='pending').update(expires_at=new_expiry)
    modeladmin.message_user(
        request,
        f"Extended expiry for {updated} approvals by 24 hours.",
        level='INFO'
    )


# ===== Toolset Configuration Actions =====

def activate_configurations(modeladmin, request, queryset):
    """Activate selected configurations."""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        f"Activated {updated} configurations.",
        level='SUCCESS'
    )


def deactivate_configurations(modeladmin, request, queryset):
    """Deactivate selected configurations."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        f"Deactivated {updated} configurations.",
        level='WARNING'
    )


def reset_usage(modeladmin, request, queryset):
    """Reset usage count for selected configurations."""
    updated = queryset.update(usage_count=0)
    modeladmin.message_user(
        request,
        f"Reset usage count for {updated} configurations.",
        level='INFO'
    )
