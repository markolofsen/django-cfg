"""Avatar field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class AvatarField(FieldConfig):
    """
    Avatar widget for displaying user avatars with fallback to initials badge.

    Automatically displays:
    - Image avatar if photo field has value
    - Colored badge with initials if no photo

    Examples:
        # Basic usage
        AvatarField(
            name="user",
            photo_field="photo_file",
            name_field="display_name",
            initials_field="first_name"
        )

        # With custom sizing and variant mapping
        AvatarField(
            name="owner",
            photo_field="avatar",
            name_field="full_name",
            initials_field="username",
            avatar_size=48,
            variant_field="user_type",  # Field to determine badge color
            variant_map={"admin": "success", "user": "secondary", "bot": "info"}
        )

        # Show as card with subtitle
        AvatarField(
            name="created_by",
            photo_field="photo",
            name_field="full_name",
            subtitle_field="email",  # Show email below name
            show_as_card=True
        )
    """

    ui_widget: Literal["avatar"] = "avatar"

    # Field mappings
    photo_field: str = Field(..., description="Model field name for photo/avatar image")
    name_field: str = Field(..., description="Model field name for display name")
    initials_field: str = Field(..., description="Model field for extracting initials (first_name, username, etc.)")
    subtitle_field: Optional[str] = Field(None, description="Optional field for subtitle (e.g., 'email', 'user_id')")

    # Display options
    avatar_size: int = Field(40, description="Avatar size in pixels (width and height)")
    show_as_card: bool = Field(False, description="Show as user card (avatar + name + subtitle)")

    # Badge fallback options
    variant_field: Optional[str] = Field(None, description="Field to determine badge variant (e.g., 'is_bot', 'user_type')")
    variant_map: Optional[Dict[Any, str]] = Field(
        None,
        description="Map field values to badge variants: {'admin': 'success', 'user': 'secondary', True: 'info', False: 'secondary'}"
    )
    default_variant: str = Field("secondary", description="Default badge variant if no mapping matches")

    # Initials extraction
    initials_max_length: int = Field(2, description="Maximum number of initials to show (1-3)")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract avatar widget configuration."""
        config = super().get_widget_config()
        config['photo_field'] = self.photo_field
        config['name_field'] = self.name_field
        config['initials_field'] = self.initials_field
        config['avatar_size'] = self.avatar_size
        config['show_as_card'] = self.show_as_card
        config['initials_max_length'] = self.initials_max_length
        config['default_variant'] = self.default_variant

        if self.subtitle_field is not None:
            config['subtitle_field'] = self.subtitle_field
        if self.variant_field is not None:
            config['variant_field'] = self.variant_field
        if self.variant_map is not None:
            config['variant_map'] = self.variant_map

        return config
