"""User field configuration."""

from typing import Any, Dict, Literal
from typing_extensions import Self

from pydantic import Field, model_validator

from .base import FieldConfig


class UserField(FieldConfig):
    """
    User display widget configuration.

    ``user_avatar`` widget requires ``header=True`` (set automatically).
    ``user_simple`` renders inline HTML without header format.

    Examples:
        UserField(name="owner", show_email=True)
        UserField(name="created_by", ui_widget="user_simple")
    """

    ui_widget: Literal["user_avatar", "user_simple"] = "user_avatar"

    show_email: bool = Field(True, description="Show user email")
    show_avatar: bool = Field(True, description="Show user avatar")
    avatar_size: int = Field(32, description="Avatar size in pixels")

    @model_validator(mode='after')
    def _auto_header_for_avatar(self) -> Self:
        """user_avatar widget returns list format — requires header=True."""
        if self.ui_widget == "user_avatar" and not self.header:
            self.header = True
        return self

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract user widget configuration."""
        config = super().get_widget_config()
        config['show_email'] = self.show_email
        config['show_avatar'] = self.show_avatar
        config['avatar_size'] = self.avatar_size
        return config
