"""ForeignKey field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from ...icons import Icons
from .base import FieldConfig


class ForeignKeyField(FieldConfig):
    """
    ForeignKey display widget with link to related object.

    Displays related object with customizable display field and optional
    link to the related object's admin page.

    Examples:
        # Basic FK display
        ForeignKeyField(
            name="machine",
            display_field="name"
        )

        # FK with custom link field
        ForeignKeyField(
            name="workspace",
            link_field="id",
            display_field="name"
        )

        # FK with admin link
        ForeignKeyField(
            name="user",
            display_field="username",
            link_to_admin=True,
            link_icon=Icons.OPEN_IN_NEW
        )

        # FK with subtitle (multiple fields)
        ForeignKeyField(
            name="machine",
            display_field="name",
            subtitle_field="hostname",
            link_to_admin=True
        )

        # FK with template subtitle
        ForeignKeyField(
            name="workspace",
            display_field="name",
            subtitle_template="{description} • {member_count} members"
        )
    """

    ui_widget: Literal["foreignkey"] = "foreignkey"

    # FK configuration
    link_field: str = Field("id", description="Field name for the link (usually 'id' or 'pk')")
    display_field: str = Field(..., description="Field name to display (e.g., 'name', 'username', 'title')")

    # Link configuration
    link_to_admin: bool = Field(True, description="Create link to admin page of related object")
    link_icon: Optional[str] = Field(None, description="Material icon to display next to link")
    link_target: str = Field("_self", description="Link target (_blank, _self, etc.)")

    # Subtitle configuration (mutually exclusive options)
    subtitle_field: Optional[str] = Field(None, description="Single field for subtitle (e.g., 'email', 'hostname')")
    subtitle_fields: Optional[list[str]] = Field(None, description="Multiple fields for subtitle")
    subtitle_template: Optional[str] = Field(
        None,
        description="Template string for subtitle with {field_name} placeholders"
    )
    subtitle_separator: str = Field(" • ", description="Separator for multiple subtitle fields")

    # Display options
    show_null_as_empty: bool = Field(True, description="Show empty value when FK is null")
    null_display: str = Field("—", description="Value to display when FK is null")

    # CSS styling
    subtitle_css_class: str = Field("text-sm text-gray-500", description="CSS classes for subtitle")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract foreignkey widget configuration."""
        config = super().get_widget_config()
        config['link_field'] = self.link_field
        config['display_field'] = self.display_field
        config['link_to_admin'] = self.link_to_admin
        config['link_target'] = self.link_target
        config['show_null_as_empty'] = self.show_null_as_empty
        config['null_display'] = self.null_display
        config['subtitle_separator'] = self.subtitle_separator
        config['subtitle_css_class'] = self.subtitle_css_class

        if self.link_icon is not None:
            config['link_icon'] = self.link_icon
        if self.subtitle_field is not None:
            config['subtitle_field'] = self.subtitle_field
        if self.subtitle_fields is not None:
            config['subtitle_fields'] = self.subtitle_fields
        if self.subtitle_template is not None:
            config['subtitle_template'] = self.subtitle_template

        return config
