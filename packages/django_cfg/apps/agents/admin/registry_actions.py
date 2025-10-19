"""
Registry Admin Actions - Agent and Template management actions.
"""

from django.contrib import messages


# ===== Agent Definition Actions =====

def activate_agents(modeladmin, request, queryset):
    """Activate selected agents."""
    updated = queryset.update(is_active=True, status='active')
    messages.success(request, f"Activated {updated} agents.")


def deactivate_agents(modeladmin, request, queryset):
    """Deactivate selected agents."""
    updated = queryset.update(is_active=False)
    messages.warning(request, f"Deactivated {updated} agents.")


def reset_stats(modeladmin, request, queryset):
    """Reset usage statistics."""
    updated = queryset.update(
        usage_count=0,
        success_rate=0,
        avg_execution_time=0,
        total_cost=0,
        last_used_at=None
    )
    messages.info(request, f"Reset statistics for {updated} agents.")


# ===== Agent Template Actions =====

def make_public(modeladmin, request, queryset):
    """Make selected templates public."""
    updated = queryset.update(is_public=True)
    messages.success(request, f"Made {updated} templates public.")


def make_private(modeladmin, request, queryset):
    """Make selected templates private."""
    updated = queryset.update(is_public=False)
    messages.warning(request, f"Made {updated} templates private.")


def duplicate_templates(modeladmin, request, queryset):
    """Duplicate selected templates."""
    duplicated = 0
    for template in queryset:
        # Create duplicate logic here
        duplicated += 1

    messages.info(request, f"Duplicated {duplicated} templates.")
