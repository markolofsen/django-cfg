"""Markdown field configuration."""

from typing import Any, Dict, Literal, Optional

from pydantic import Field

from ...icons import Icons
from .base import FieldConfig


class MarkdownField(FieldConfig):
    """
    Markdown documentation widget configuration.

    Renders markdown content from field value or external file with beautiful styling.
    Auto-detects whether content is a file path or markdown string.

    Examples:
        # From model field (markdown string)
        MarkdownField(
            name="description",
            title="Documentation",
            collapsible=True
        )

        # From file path field
        MarkdownField(
            name="docs_path",
            title="User Guide",
            collapsible=True,
            default_open=True
        )

        # Static file (same for all objects)
        MarkdownField(
            name="static_doc",  # method that returns file path
            title="API Documentation",
            source_file="docs/api.md",  # relative to app root
            max_height="500px"
        )

        # Dynamic markdown with custom title
        MarkdownField(
            name="get_help_text",  # method that generates markdown
            title="Help",
            collapsible=True,
            enable_plugins=True
        )
    """

    ui_widget: Literal["markdown"] = "markdown"

    # Display options
    collapsible: bool = Field(True, description="Wrap in collapsible details/summary")
    default_open: bool = Field(False, description="Open by default if collapsible")
    max_height: Optional[str] = Field("500px", description="Max height with scrolling (e.g., '500px', None for no limit)")
    full_width: bool = Field(True, description="Span full width of fieldset (default: True)")

    # Content source
    source_file: Optional[str] = Field(
        None,
        description="Static file path relative to app root (e.g., 'docs/api.md')"
    )
    source_field: Optional[str] = Field(
        None,
        description="Alternative field name for content (defaults to 'name' field)"
    )

    # Markdown options
    enable_plugins: bool = Field(
        True,
        description="Enable mistune plugins (tables, strikethrough, task lists, etc.)"
    )

    # Custom icon for collapsible header
    header_icon: Optional[str] = Field(
        Icons.DESCRIPTION,
        description="Material icon for collapsible header"
    )

    def get_widget_config(self) -> Dict[str, Any]:
        """Extract markdown widget configuration."""
        config = super().get_widget_config()
        config['collapsible'] = self.collapsible
        config['default_open'] = self.default_open
        config['max_height'] = self.max_height
        config['enable_plugins'] = self.enable_plugins
        config['full_width'] = self.full_width

        if self.source_file is not None:
            config['source_file'] = self.source_file
        if self.source_field is not None:
            config['source_field'] = self.source_field
        if self.header_icon is not None:
            config['header_icon'] = self.header_icon

        return config
