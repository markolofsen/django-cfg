"""Counter badge field configuration for count + link badges."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class CounterBadgeField(FieldConfig):
    """
    Display a badge with counter value and optional link.

    Perfect for showing counts (messages, views, etc.) with links to filtered lists.
    Automatically formats large numbers with thousands separator.

    Examples:
        # Messages count with link to filtered messages
        CounterBadgeField(
            name="messages_badge",
            title="Messages",
            count_field="messages_count",
            variant="primary",
            icon=Icons.MESSAGE,
            link_url_template="/admin/app/message/?user_id={obj.id}",
            empty_display=True,  # Show "-" when count is 0
        )

        # Simple counter without link
        CounterBadgeField(
            name="views_count",
            title="Views",
            count_field="view_count",
            variant="info",
            icon=Icons.VISIBILITY,
            format_thousands=True,  # 1,234 instead of 1234
        )

        # Conditional formatting based on count
        CounterBadgeField(
            name="errors_badge",
            title="Errors",
            count_field="error_count",
            variant="danger",
            icon=Icons.ERROR,
            hide_on_zero=True,  # Don't show badge if count is 0
        )
    """

    ui_widget: Literal["counter_badge"] = "counter_badge"

    # Counter configuration
    count_field: str = Field(
        ...,
        description="Model field name containing the count value"
    )

    # Badge styling
    variant: Literal["primary", "secondary", "success", "danger", "warning", "info"] = Field(
        "primary",
        description="Badge color variant"
    )
    icon: Optional[str] = Field(
        None,
        description="Material icon name (from Icons class)"
    )

    # Link configuration
    link_url_template: Optional[str] = Field(
        None,
        description="URL template with {obj.field} placeholders (e.g., '/admin/app/model/?filter={obj.id}')"
    )
    link_target: str = Field(
        "_self",
        description="Link target (_self, _blank, etc.)"
    )

    # Formatting options
    format_thousands: bool = Field(
        True,
        description="Format numbers with thousands separator (1,234)"
    )

    # Empty state handling
    hide_on_zero: bool = Field(
        False,
        description="Hide badge completely when count is 0"
    )
    empty_display: bool = Field(
        False,
        description="Show empty indicator (dash) when count is 0 instead of hiding"
    )
    empty_text: str = Field(
        "-",
        description="Text to show when count is 0 (if empty_display=True)"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract counter badge widget configuration."""
        config = super().get_widget_config()

        config['count_field'] = self.count_field
        config['variant'] = self.variant
        config['format_thousands'] = self.format_thousands
        config['hide_on_zero'] = self.hide_on_zero
        config['empty_display'] = self.empty_display
        config['empty_text'] = self.empty_text
        config['link_target'] = self.link_target

        if self.icon is not None:
            config['icon'] = self.icon

        if self.link_url_template is not None:
            config['link_url_template'] = self.link_url_template

        return config
