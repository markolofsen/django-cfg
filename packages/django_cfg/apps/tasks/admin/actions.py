"""
Task admin actions.
"""

from django.contrib import messages


def retry_failed_tasks(modeladmin, request, queryset):
    """Retry selected failed tasks."""
    failed_tasks = queryset.filter(status='failed')
    count = failed_tasks.count()

    if count > 0:
        # Here you would implement the retry logic
        messages.success(request, f"Queued {count} tasks for retry.")
    else:
        messages.warning(request, "No failed tasks selected.")


def cancel_pending_tasks(modeladmin, request, queryset):
    """Cancel selected pending tasks."""
    pending_tasks = queryset.filter(status='pending')
    count = pending_tasks.count()

    if count > 0:
        pending_tasks.update(status='cancelled')
        messages.success(request, f"Cancelled {count} pending tasks.")
    else:
        messages.warning(request, "No pending tasks selected.")
