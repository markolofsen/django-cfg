"""
List display builders for admin list view.

Builds list_display, list_display_links and generates display methods.
"""

import logging
from typing import TYPE_CHECKING, Any, List

from django.utils.safestring import mark_safe

from ...widgets import WidgetRegistry

if TYPE_CHECKING:
    from ...config import AdminConfig

logger = logging.getLogger(__name__)


def _get_nested_value(obj: Any, field_name: str) -> Any:
    """Get value from possibly nested field (e.g., 'cdn_file__file')."""
    if '__' not in field_name:
        return getattr(obj, field_name, None)

    parts = field_name.split("__")
    value = obj
    for part in parts:
        if value is None:
            return None
        value = getattr(value, part, None)
    return value


def build_list_display(cls, config: 'AdminConfig') -> List[str]:
    """
    Build list_display with generated display methods.

    Args:
        cls: The admin class to add methods to
        config: AdminConfig instance

    Returns:
        List of field names for list_display
    """
    result = []
    # Get list_display_links for detecting link fields
    link_fields = config.list_display_links or []

    for field_name in config.list_display:
        # Check if we have a FieldConfig for this field
        field_config = config.get_display_field_config(field_name)

        if field_config and field_config.ui_widget:
            # Check if this field is a link field
            is_link = field_name in link_fields
            # Generate display method for this field
            method_name = f"{field_name}_display"
            display_method = generate_display_method(field_config, is_link=is_link)
            setattr(cls, method_name, display_method)
            result.append(method_name)
        else:
            # Use field as-is
            result.append(field_name)

    return result


def build_list_display_links(config: 'AdminConfig') -> List[str]:
    """
    Build list_display_links with correct field names.

    If a field has a display_field config with ui_widget, it will be renamed
    to {field_name}_display in list_display. We need to apply the same
    transformation to list_display_links so Django can find the matching field.

    Args:
        config: AdminConfig instance

    Returns:
        List of field names for list_display_links
    """
    result = []

    for field_name in config.list_display_links:
        # Check if we have a FieldConfig for this field
        field_config = config.get_display_field_config(field_name)

        if field_config and field_config.ui_widget:
            # Field was renamed to {field_name}_display
            result.append(f"{field_name}_display")
        else:
            # Use field as-is
            result.append(field_name)

    return result


def generate_display_method(field_config, is_link: bool = False):
    """
    Generate display method from FieldConfig.

    Args:
        field_config: FieldConfig instance
        is_link: Whether this field is in list_display_links

    Returns:
        Display method function
    """

    def display_method(self, obj):
        # Get field value (supports __ notation for FK traversal)
        value = _get_nested_value(obj, field_config.name)

        # For LinkField, value comes from link_field, not name - skip early return
        # Also skip for fields with static_text
        # Also skip for composite fields like StackedField that use virtual names
        # Also skip for fields with fallback_field (e.g., ImagePreviewField)
        has_link_field = hasattr(field_config, 'link_field') and field_config.link_field
        has_static_text = hasattr(field_config, 'static_text') and field_config.static_text
        has_rows = hasattr(field_config, 'rows') and field_config.rows  # StackedField
        has_fallback_field = hasattr(field_config, 'fallback_field') and field_config.fallback_field

        if value is None and not has_link_field and not has_static_text and not has_rows and not has_fallback_field:
            empty = field_config.empty_value
            # For header fields, return tuple format
            if field_config.header:
                return (empty, [])
            return empty

        # Render using widget
        if field_config.ui_widget:
            widget_config = field_config.get_widget_config()
            # Add is_link flag for link styling
            widget_config['is_link'] = is_link
            rendered = WidgetRegistry.render(
                field_config.ui_widget,
                obj,
                field_config.name,
                widget_config
            )

            # Widget returns the result - could be string, list, or tuple
            # For header widgets (user_avatar), they return list format directly
            # For other widgets, wrap in safe string
            if rendered is None:
                rendered = field_config.empty_value

            # If it's already a list or tuple (e.g., from user_avatar widget), return as-is
            if isinstance(rendered, (list, tuple)):
                return rendered

            # Otherwise mark as safe and return
            result = mark_safe(rendered)

            # For non-list header fields, wrap in tuple format
            if field_config.header:
                return (result, [])
            return result

        # Fallback to simple value
        if field_config.header:
            return (value, [])
        return value

    # Set display method attributes
    display_method.short_description = field_config.title or field_config.name.replace('_', ' ').title()

    if field_config.ordering:
        display_method.admin_order_field = field_config.ordering

    # Check if field has boolean attribute (only for BooleanField or base FieldConfig)
    if hasattr(field_config, 'boolean') and field_config.boolean:
        display_method.boolean = True

    if field_config.header:
        # For header display (user with avatar)
        display_method.header = True

    return display_method
