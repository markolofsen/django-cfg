"""User field configuration."""

from typing import Any, Dict, Literal

from pydantic import Field

from .base import FieldConfig


class UserField(FieldConfig):
    """
    User display widget configuration.

    Examples:
        UserField(name="owner", ui_widget="user_avatar", show_email=True)
        UserField(name="created_by", ui_widget="user_simple")
    """

    ui_widget: Literal["user_avatar", "user_simple"] = "user_avatar"

    show_email: bool = Field(True, description="Show user email")
    show_avatar: bool = Field(True, description="Show user avatar")
    avatar_size: int = Field(32, description="Avatar size in pixels")

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract user widget configuration."""
        config = super().get_widget_config()
        config['show_email'] = self.show_email
        config['show_avatar'] = self.show_avatar
        config['avatar_size'] = self.avatar_size
        return config
