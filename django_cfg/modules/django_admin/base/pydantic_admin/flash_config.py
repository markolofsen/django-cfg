"""
Pydantic v2 models for flash message configuration and session payloads.

Provides type-safe alternatives to raw dicts for:
- FlashPayload: session-stored flash data
- FlashFieldConfig: declarative one_time_flash_fields entry
- FlashStyle: Literal type for valid style keys
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# All valid flash display styles
FlashStyle = Literal[
    "code_warning",
    "code_error",
    "code_success",
    "info",
    "warning",
    "error",
    "success",
    "raw",
]


class FlashPayload(BaseModel):
    """
    One-time flash message payload stored in Django's session.

    Validated on write (flash_once) and on read (display method).
    Ensures session data is always well-formed.

    Session key format:
        _pydantic_admin_flash_{app_label}_{model_name}_{pk}_{field_name}
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    content: str = Field(..., description="Main sensitive content to display (e.g. API key)")
    title: str = Field(default="", description="Bold header shown above content box")
    message: str = Field(default="", description="Subtitle/instruction text")
    style: FlashStyle = Field(
        default="code_warning",
        description="Visual style key controlling box appearance",
    )


class FlashFieldConfig(BaseModel):
    """
    Configuration for a single declarative one-time flash field.

    Used in the `one_time_flash_fields` class attribute of PydanticAdmin subclasses:

        class MyAdmin(PydanticAdmin):
            one_time_flash_fields = {
                'plain_key_display': FlashFieldConfig(
                    source='_generated_plain_key',
                    style='code_warning',
                    title='Plain API Key (One-Time Display)',
                    message='SAVE THIS KEY NOW',
                )
            }

    PydanticAdmin reads `source` attribute from the model object after save_model()
    and calls flash_once() automatically.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    source: str = Field(
        ...,
        description="Transient model attribute to read content from (e.g. '_generated_plain_key')",
    )
    style: FlashStyle = Field(
        default="code_warning",
        description="Visual style for display box",
    )
    title: str = Field(
        default="",
        description="Bold header shown above content",
    )
    message: str = Field(
        default="",
        description="Subtitle/instruction shown below title",
    )

    def to_payload(self, content: str) -> FlashPayload:
        """Create a FlashPayload from this config and a content value."""
        return FlashPayload(
            content=content,
            title=self.title,
            message=self.message,
            style=self.style,
        )


__all__ = [
    "FlashStyle",
    "FlashPayload",
    "FlashFieldConfig",
]
