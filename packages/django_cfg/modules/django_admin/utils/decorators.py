"""
Decorators for Django Admin display methods.

Provides convenient decorators to simplify custom display method creation.
"""

from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from django.utils.safestring import SafeString, mark_safe


def _ensure_safe_html(value):
    """
    Ensure HTML strings are marked as safe.

    If value is already SafeString, return as-is.
    If value is a string containing HTML tags, mark it as safe.
    Otherwise return value unchanged.
    """
    if isinstance(value, SafeString):
        # Already safe
        return value

    if isinstance(value, str) and ('<' in value or '&' in value):
        # Looks like HTML, mark as safe
        return mark_safe(value)

    # Not HTML or not a string
    return value


def computed_field(
    short_description: str,
    ordering: Optional[str] = None,
    boolean: bool = False,
    allow_tags: bool = False,
    empty_value: str = "—",
    admin_order_field: Optional[str] = None,
):
    """
    Decorator for admin display methods that compute values from the model instance.

    Simplifies creation of custom display methods by automatically setting common attributes.

    Args:
        short_description: The column header text in the admin list view
        ordering: Field name to use for ordering (alternative to admin_order_field)
        boolean: Whether this field should be displayed as a boolean icon
        allow_tags: Whether HTML tags are allowed (deprecated in Django, use format_html instead)
        empty_value: Value to display when the computed value is None or empty
        admin_order_field: Field name to use for sorting (legacy name)

    Usage:
        @computed_field("Full Name", ordering="last_name")
        def full_name(self, obj):
            return f"{obj.first_name} {obj.last_name}"

        @computed_field("Is Active", boolean=True)
        def is_active_display(self, obj):
            return obj.is_active

        @computed_field("Status Badge", allow_tags=True)
        def status_badge(self, obj):
            return format_html('<span class="badge">{}</span>', obj.status)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, obj):
            result = func(self, obj)

            # Handle empty values
            if result is None or result == "":
                return empty_value

            # Ensure HTML is marked as safe
            return _ensure_safe_html(result)

        # Set display method attributes
        wrapper.short_description = short_description

        # Set ordering field (prefer ordering parameter, fallback to admin_order_field)
        if ordering:
            wrapper.admin_order_field = ordering
        elif admin_order_field:
            wrapper.admin_order_field = admin_order_field

        if boolean:
            wrapper.boolean = True

        if allow_tags:
            wrapper.allow_tags = True

        return wrapper

    return decorator


def badge_field(
    short_description: str,
    label_map: Optional[Dict[Any, str]] = None,
    ordering: Optional[str] = None,
    empty_value: str = "—",
):
    """
    Decorator for fields that display badges based on value-to-variant mapping.

    Automatically renders values as badges with appropriate styling.

    Args:
        short_description: The column header text
        label_map: Mapping of field values to badge variants (e.g., {"active": "success", "inactive": "secondary"})
        ordering: Field name to use for ordering
        empty_value: Value to display when field is None or empty

    Usage:
        @badge_field("Status", label_map={"active": "success", "inactive": "secondary"}, ordering="status")
        def status_badge(self, obj):
            from django_cfg.modules.django_admin.utils.badges import StatusBadge
            from django_cfg.modules.django_admin.models.badge_models import StatusBadgeConfig

            if not obj.status:
                return None

            variant = self.status_badge.label_map.get(obj.status, "secondary")
            return StatusBadge.create(
                text=obj.status.title(),
                variant=variant,
                config=StatusBadgeConfig()
            )

    Note: The actual badge rendering must be done inside the method using StatusBadge or similar utilities.
    This decorator just provides the infrastructure (ordering, empty values, label_map storage).
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, obj):
            result = func(self, obj)

            if result is None or result == "":
                return empty_value

            # Ensure HTML is marked as safe (badges always contain HTML)
            return _ensure_safe_html(result)

        # Set attributes
        wrapper.short_description = short_description
        wrapper.allow_tags = True  # Badges use HTML

        if ordering:
            wrapper.admin_order_field = ordering

        # Store label_map on the function for access inside the method
        if label_map:
            wrapper.label_map = label_map

        return wrapper

    return decorator


def currency_field(
    short_description: str,
    currency: str = "USD",
    precision: int = 2,
    ordering: Optional[str] = None,
    empty_value: str = "—",
):
    """
    Decorator for currency display fields.

    Formats numeric values as currency with appropriate symbol and precision.

    Args:
        short_description: The column header text
        currency: Currency code (USD, EUR, etc.)
        precision: Number of decimal places
        ordering: Field name to use for ordering
        empty_value: Value to display when field is None

    Usage:
        @currency_field("Balance", currency="USD", precision=2, ordering="balance")
        def balance_display(self, obj):
            if obj.balance is None:
                return None
            return f"${obj.balance:.2f}"
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, obj):
            result = func(self, obj)

            if result is None:
                return empty_value

            # Ensure HTML is marked as safe if needed
            return _ensure_safe_html(result)

        # Set attributes
        wrapper.short_description = short_description

        if ordering:
            wrapper.admin_order_field = ordering

        # Store currency config
        wrapper.currency = currency
        wrapper.precision = precision

        return wrapper

    return decorator


def annotated_field(
    short_description: str,
    annotation_name: str,
    ordering: Optional[str] = None,
    empty_value: str = "—",
):
    """
    Decorator for fields that display annotated values from the queryset.

    Marks that the field depends on a queryset annotation.

    Args:
        short_description: The column header text
        annotation_name: Name of the annotation in the queryset
        ordering: Field name to use for ordering (defaults to annotation_name)
        empty_value: Value to display when annotation result is None

    Usage:
        # In AdminConfig:
        annotations = {
            'total_orders': Count('orders')
        }

        # In Admin class:
        @annotated_field("Total Orders", annotation_name="total_orders")
        def order_count(self, obj):
            count = getattr(obj, 'total_orders', 0)
            return f"{count} orders"
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, obj):
            # Get annotated value
            value = getattr(obj, annotation_name, None)

            if value is None:
                return empty_value

            result = func(self, obj)

            if result is None or result == "":
                return empty_value

            # Ensure HTML is marked as safe if needed
            return _ensure_safe_html(result)

        # Set attributes
        wrapper.short_description = short_description
        wrapper.annotation_name = annotation_name

        # Default ordering to annotation name
        if ordering:
            wrapper.admin_order_field = ordering
        else:
            wrapper.admin_order_field = annotation_name

        return wrapper

    return decorator
