"""
Balance admin actions.

Standalone action handlers for Balance admin.
"""


def reset_zero_balances(modeladmin, request, queryset):
    """Reset balances that are zero."""
    updated = queryset.filter(balance_usd=0).update(
        total_deposited=0,
        total_withdrawn=0
    )
    modeladmin.message_user(
        request,
        f"Successfully reset {updated} zero balance(s).",
        level='WARNING'
    )
