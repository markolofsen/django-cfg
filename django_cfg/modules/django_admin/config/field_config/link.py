"""Link field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from ...icons import Icons
from .base import FieldConfig


class LinkField(FieldConfig):
    """
    Text with external link and optional icon/subtitle.

    Universal field for displaying clickable text with links to external resources,
    optional icons, and subtitle information.

    Examples:
        # Basic link
        LinkField(
            name="display_name",
            link_field="telegram_link"
        )

        # Link with icon
        LinkField(
            name="username",
            link_field="profile_url",
            link_icon=Icons.OPEN_IN_NEW,
            link_target="_blank"
        )

        # Link with subtitle from single field
        LinkField(
            name="display_name",
            link_field="telegram_link",
            link_icon=Icons.OPEN_IN_NEW,
            subtitle_field="phone"
        )

        # Link with subtitle from multiple fields
        LinkField(
            name="display_name",
            link_field="telegram_link",
            link_icon=Icons.OPEN_IN_NEW,
            subtitle_fields=["full_name", "phone"],
            subtitle_separator=" • "
        )

        # Link with template subtitle
        LinkField(
            name="channel_title",
            link_field="channel_url",
            link_icon=Icons.OPEN_IN_NEW,
            subtitle_template="ID: {channel_id} • Subscribers: {subscriber_count}"
        )
    """

    ui_widget: Literal["link"] = "link"

    # Link configuration
    link_field: str = Field(..., description="Model field name containing the URL")
    link_icon: Optional[str] = Field(Icons.OPEN_IN_NEW, description="Material icon to display next to link")
    link_target: str = Field("_blank", description="Link target (_blank, _self, etc.)")
    static_text: Optional[str] = Field(None, description="Static text to display instead of field value")

    # Subtitle configuration (mutually exclusive options)
    subtitle_field: Optional[str] = Field(None, description="Single field for subtitle (e.g., 'phone', 'email')")
    subtitle_fields: Optional[list[str]] = Field(None, description="Multiple fields for subtitle (e.g., ['full_name', 'phone'])")
    subtitle_template: Optional[str] = Field(
        None,
        description="Template string for subtitle with {field_name} placeholders (e.g., 'ID: {user_id}')"
    )
    subtitle_separator: str = Field(" • ", description="Separator for multiple subtitle fields")

    # CSS styling
    subtitle_css_class: str = Field("text-sm text-gray-500", description="CSS classes for subtitle")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract link widget configuration."""
        config = super().get_widget_config()
        config['link_field'] = self.link_field
        config['link_target'] = self.link_target
        config['subtitle_separator'] = self.subtitle_separator
        config['subtitle_css_class'] = self.subtitle_css_class

        if self.link_icon is not None:
            config['link_icon'] = self.link_icon
        if self.static_text is not None:
            config['static_text'] = self.static_text
        if self.subtitle_field is not None:
            config['subtitle_field'] = self.subtitle_field
        if self.subtitle_fields is not None:
            config['subtitle_fields'] = self.subtitle_fields
        if self.subtitle_template is not None:
            config['subtitle_template'] = self.subtitle_template

        return config
