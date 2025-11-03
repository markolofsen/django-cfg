"""
Admin actions for Payments app.

Standalone action handlers for use with new Pydantic admin.
"""


def activate_currencies(modeladmin, request, queryset):
    """Activate selected currencies."""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"Activated {updated} currency(ies).", level='SUCCESS')


def deactivate_currencies(modeladmin, request, queryset):
    """Deactivate selected currencies."""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"Deactivated {updated} currency(ies).", level='WARNING')
