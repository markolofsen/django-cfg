"""
Execution admin actions.

Standalone action handlers for Agent Execution and Workflow Execution admins.
"""

from django_cfg.modules.django_logging import get_logger

logger = get_logger("execution_admin")


# ===== Agent Execution Actions =====

def retry_failed_executions(modeladmin, request, queryset):
    """Retry failed executions."""
    failed_count = queryset.filter(status='failed').count()
    modeladmin.message_user(
        request,
        f"Retry functionality not implemented yet. {failed_count} failed executions selected.",
        level='WARNING'
    )


def clear_cache(modeladmin, request, queryset):
    """Clear cache for selected executions."""
    cached_count = queryset.filter(cached=True).count()
    modeladmin.message_user(
        request,
        f"Cache clearing not implemented yet. {cached_count} cached executions selected.",
        level='INFO'
    )


# ===== Workflow Execution Actions =====

def cancel_running_workflows(modeladmin, request, queryset):
    """Cancel running workflows."""
    running_count = queryset.filter(status='running').count()
    modeladmin.message_user(
        request,
        f"Cancel functionality not implemented yet. {running_count} running workflows selected.",
        level='WARNING'
    )


def retry_failed_workflows(modeladmin, request, queryset):
    """Retry failed workflows."""
    failed_count = queryset.filter(status='failed').count()
    modeladmin.message_user(
        request,
        f"Retry functionality not implemented yet. {failed_count} failed workflows selected.",
        level='WARNING'
    )
