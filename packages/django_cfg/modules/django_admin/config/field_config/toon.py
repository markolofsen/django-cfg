"""TOON/JSON viewer field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from .base import FieldConfig


class ToonField(FieldConfig):
    """
    JSON field rendered as TOON (Token-Oriented Object Notation) with JSON fallback.

    In list_display: compact preview with Alpine.js expand/collapse.
    In readonly_fields: full collapsible <details> block with JSON↔TOON toggle.

    The selected mode (JSON/TOON) is persisted in localStorage — user's preference
    is remembered across all admin pages.

    Examples::

        # In list_display
        ToonField(name="metadata")
        ToonField(name="settings", preview_lines=5)

        # In readonly_fields (full collapsible)
        ToonField(
            name="raw_data",
            collapsible=True,
            default_mode="toon",
            label="Request payload",
        )
    """

    ui_widget: Literal["toon_viewer"] = "toon_viewer"

    # Collapsible (for change form readonly view)
    collapsible: bool = Field(True, description="Wrap in collapsible <details>/<summary>")
    default_open: bool = Field(False, description="Open by default when collapsible=True")

    # Mode
    default_mode: Literal["toon", "json"] = Field(
        "toon",
        description="Default display mode — 'toon' or 'json'. Persisted in localStorage.",
    )

    # List display options
    preview_lines: int = Field(3, description="Lines visible in list_display before expand", ge=1, le=20)

    # Form display options
    label: Optional[str] = Field(None, description="Header label in <details> (defaults to field title)")
    max_height: str = Field("24rem", description="Max height of content area (CSS value)")

    def get_widget_config(self) -> Dict[str, Any]:
        config = super().get_widget_config()
        config["collapsible"] = self.collapsible
        config["default_open"] = self.default_open
        config["default_mode"] = self.default_mode
        config["preview_lines"] = self.preview_lines
        config["label"] = self.label or self.title or self.name
        config["max_height"] = self.max_height
        return config
