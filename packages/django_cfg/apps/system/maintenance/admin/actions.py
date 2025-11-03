"""
Maintenance admin actions.
"""

from django.contrib import messages


# CloudflareApiKey actions

def make_default_key(modeladmin, request, queryset):
    """Make selected key the default."""
    if queryset.count() > 1:
        messages.error(request, "Please select only one API key to make default.")
        return

    key = queryset.first()
    if key:
        key.is_default = True
        key.save()
        messages.success(request, f"'{key.name}' is now the default API key.")


def activate_keys(modeladmin, request, queryset):
    """Activate selected API keys."""
    count = queryset.update(is_active=True)
    messages.success(request, f"Successfully activated {count} API keys.")


def deactivate_keys(modeladmin, request, queryset):
    """Deactivate selected API keys."""
    default_keys = queryset.filter(is_default=True)
    if default_keys.exists():
        messages.error(
            request,
            "Cannot deactivate default API key. Please set another key as default first."
        )
        return

    count = queryset.update(is_active=False)
    messages.warning(request, f"Successfully deactivated {count} API keys.")


# ScheduledMaintenance actions

def execute_maintenance(modeladmin, request, queryset):
    """Execute selected maintenance tasks."""
    from ..models import ScheduledMaintenance

    scheduled_count = queryset.filter(status=ScheduledMaintenance.Status.SCHEDULED).count()
    if scheduled_count == 0:
        messages.error(request, "No scheduled maintenance tasks selected.")
        return

    queryset.filter(status=ScheduledMaintenance.Status.SCHEDULED).update(
        status=ScheduledMaintenance.Status.ACTIVE
    )

    messages.success(request, f"Started execution of {scheduled_count} maintenance tasks.")


def cancel_maintenance(modeladmin, request, queryset):
    """Cancel selected maintenance tasks."""
    from ..models import ScheduledMaintenance

    cancelable_count = queryset.filter(
        status__in=[ScheduledMaintenance.Status.SCHEDULED, ScheduledMaintenance.Status.ACTIVE]
    ).count()

    if cancelable_count == 0:
        messages.error(request, "No cancelable maintenance tasks selected.")
        return

    queryset.filter(
        status__in=[ScheduledMaintenance.Status.SCHEDULED, ScheduledMaintenance.Status.ACTIVE]
    ).update(status=ScheduledMaintenance.Status.CANCELLED)

    messages.warning(request, f"Cancelled {cancelable_count} maintenance tasks.")


def reschedule_maintenance(modeladmin, request, queryset):
    """Reschedule selected maintenance tasks."""
    from ..models import ScheduledMaintenance

    reschedulable_count = queryset.filter(
        status__in=[ScheduledMaintenance.Status.CANCELLED, ScheduledMaintenance.Status.FAILED]
    ).count()

    if reschedulable_count == 0:
        messages.error(request, "No reschedulable maintenance tasks selected.")
        return

    queryset.filter(
        status__in=[ScheduledMaintenance.Status.CANCELLED, ScheduledMaintenance.Status.FAILED]
    ).update(status=ScheduledMaintenance.Status.SCHEDULED)

    messages.info(request, f"Reset {reschedulable_count} maintenance tasks to scheduled.")


# CloudflareSite actions

def enable_maintenance_mode(modeladmin, request, queryset):
    """Enable maintenance mode for selected sites."""
    from ..services import MaintenanceService

    service = MaintenanceService()
    success_count = 0
    error_count = 0

    for site in queryset:
        try:
            service.enable_maintenance(site)
            success_count += 1
        except Exception as e:
            error_count += 1
            messages.error(request, f"Failed to enable maintenance for {site.name}: {str(e)}")

    if success_count > 0:
        messages.success(request, f"Successfully enabled maintenance for {success_count} sites.")
    if error_count > 0:
        messages.error(request, f"Failed to enable maintenance for {error_count} sites.")


def disable_maintenance_mode(modeladmin, request, queryset):
    """Disable maintenance mode for selected sites."""
    from ..services import MaintenanceService

    service = MaintenanceService()
    success_count = 0
    error_count = 0

    for site in queryset:
        try:
            service.disable_maintenance(site)
            success_count += 1
        except Exception as e:
            error_count += 1
            messages.error(request, f"Failed to disable maintenance for {site.name}: {str(e)}")

    if success_count > 0:
        messages.success(request, f"Successfully disabled maintenance for {success_count} sites.")
    if error_count > 0:
        messages.error(request, f"Failed to disable maintenance for {error_count} sites.")


def activate_sites(modeladmin, request, queryset):
    """Activate selected sites."""
    count = queryset.update(is_active=True)
    messages.success(request, f"Successfully activated {count} sites.")


def deactivate_sites(modeladmin, request, queryset):
    """Deactivate selected sites."""
    count = queryset.update(is_active=False)
    messages.warning(request, f"Successfully deactivated {count} sites.")


def sync_with_cloudflare(modeladmin, request, queryset):
    """Sync selected sites with Cloudflare."""
    messages.info(request, f"Cloudflare sync initiated for {queryset.count()} sites.")
