"""
Markdown integration for HTML builder.

Provides thin wrapper methods that delegate to MarkdownRenderer.
"""

from pathlib import Path
from typing import Optional, Union

from django.utils.safestring import SafeString


class MarkdownIntegration:
    """Markdown rendering integration for HtmlBuilder."""

    @staticmethod
    def markdown(
        text: str,
        css_class: str = "",
        max_height: Optional[str] = None,
        enable_plugins: bool = True
    ) -> SafeString:
        """
        Render markdown text to beautifully styled HTML.

        Delegates to MarkdownRenderer.render_markdown() for actual rendering.

        Args:
            text: Markdown content
            css_class: Additional CSS classes
            max_height: Max height with scrolling (e.g., "400px", "20rem")
            enable_plugins: Enable mistune plugins (tables, strikethrough, etc.)

        Usage:
            # Simple markdown rendering
            html.markdown("# Hello\\n\\nThis is **bold** text")

            # With custom styling
            html.markdown(obj.description, css_class="my-custom-class")

            # With max height for long content
            html.markdown(obj.documentation, max_height="500px")

        Returns:
            SafeString with rendered HTML
        """
        # Import here to avoid circular dependency
        from ..markdown.renderer import MarkdownRenderer

        return MarkdownRenderer.render_markdown(
            text=text,
            css_class=css_class,
            max_height=max_height,
            enable_plugins=enable_plugins
        )

    @staticmethod
    def markdown_docs(
        content: Union[str, Path],
        collapsible: bool = True,
        title: str = "Documentation",
        icon: str = "description",
        max_height: Optional[str] = "500px",
        enable_plugins: bool = True,
        default_open: bool = False
    ) -> SafeString:
        """
        Render markdown documentation from string or file with collapsible UI.

        Auto-detects whether content is a file path or markdown string.

        Args:
            content: Markdown string or path to .md file
            collapsible: Wrap in collapsible details/summary
            title: Title for collapsible section
            icon: Material icon name for title
            max_height: Max height for scrolling
            enable_plugins: Enable markdown plugins
            default_open: Open by default if collapsible

        Usage:
            # From string with collapse
            html.markdown_docs(obj.description, title="Description")

            # From file
            html.markdown_docs("docs/api.md", title="API Documentation")

            # Simple, no collapse
            html.markdown_docs(obj.notes, collapsible=False)

            # Open by default
            html.markdown_docs(obj.readme, default_open=True)

        Returns:
            Rendered markdown with beautiful Tailwind styling
        """
        # Import here to avoid circular dependency
        from ..markdown.renderer import MarkdownRenderer

        return MarkdownRenderer.render(
            content=content,
            collapsible=collapsible,
            title=title,
            icon=icon,
            max_height=max_height,
            enable_plugins=enable_plugins,
            default_open=default_open
        )
