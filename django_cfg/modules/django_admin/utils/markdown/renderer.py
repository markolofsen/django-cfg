"""
Markdown rendering service for Django Admin.

Provides utilities for rendering markdown content from strings or files
with beautiful Tailwind CSS styling and collapsible sections.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional, Union

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString, mark_safe

logger = logging.getLogger(__name__)

try:
    import mistune
    MISTUNE_AVAILABLE = True
except ImportError:
    MISTUNE_AVAILABLE = False


class MarkdownRenderer:
    """
    Markdown rendering service with file/string support and collapsible UI.

    Features:
        - Render markdown from strings or .md files
        - Auto-detect content type (file path vs markdown string)
        - Beautiful Tailwind CSS styling with dark mode
        - Collapsible sections for documentation
        - Support for all markdown features (tables, code blocks, etc.)

    Usage:
        # In admin.py
        from django_cfg.modules.django_admin.utils import MarkdownRenderer

        class MyAdmin(admin.ModelAdmin):
            def documentation(self, obj):
                # From file
                return MarkdownRenderer.render(obj.docs_file_path, collapsible=True)

                # From string
                return MarkdownRenderer.render(obj.markdown_content, collapsible=True)

                # From field or string with custom title
                return MarkdownRenderer.render(
                    obj.description,
                    collapsible=True,
                    title="Description"
                )
    """

    # Singleton markdown parser instances
    _md_with_plugins = None
    _md_without_plugins = None

    @classmethod
    def _get_markdown_parser(cls, enable_plugins: bool = True, enable_mermaid: bool = True):
        """
        Get or create markdown parser instance (singleton pattern).

        Args:
            enable_plugins: Enable standard mistune plugins
            enable_mermaid: Enable Mermaid diagram support
        """
        if not MISTUNE_AVAILABLE:
            return None

        if enable_plugins:
            if cls._md_with_plugins is None:
                # Import Mermaid plugin
                from .mermaid_plugin import mermaid_plugin

                # Create markdown with standard plugins
                md = mistune.create_markdown(
                    plugins=['strikethrough', 'table', 'url', 'task_lists', 'def_list']
                )

                # Add Mermaid plugin if enabled
                if enable_mermaid:
                    md = mermaid_plugin(md)

                cls._md_with_plugins = md
            return cls._md_with_plugins
        else:
            if cls._md_without_plugins is None:
                cls._md_without_plugins = mistune.create_markdown()
            return cls._md_without_plugins

    @classmethod
    def _load_from_file(cls, file_path: Union[str, Path]) -> Optional[str]:
        """
        Load markdown content from file.

        Args:
            file_path: Path to .md file

        Returns:
            File content or None if error
        """
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"Markdown file not found: {file_path}")
                return None

            if not path.suffix.lower() in ['.md', '.markdown']:
                logger.warning(f"File is not a markdown file: {file_path}")
                return None

            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading markdown file {file_path}: {e}")
            return None

    @classmethod
    def _is_file_path(cls, content: str) -> bool:
        """
        Check if content is a file path.

        Args:
            content: String to check

        Returns:
            True if looks like a file path
        """
        # Check if it's a valid path and file exists
        if '\n' in content:
            return False  # Multi-line content is not a file path

        try:
            path = Path(content)
            return path.exists() and path.is_file() and path.suffix.lower() in ['.md', '.markdown']
        except (OSError, ValueError):
            return False

    @classmethod
    def render_markdown(
        cls,
        text: str,
        css_class: str = "",
        max_height: Optional[str] = None,
        enable_plugins: bool = True
    ) -> SafeString:
        """
        Render markdown text to HTML (``cfg-markdown`` container).

        Args:
            text: Markdown content
            css_class: Additional CSS classes
            max_height: Max height with scrolling (e.g., "400px", "20rem")
            enable_plugins: Enable mistune plugins (tables, strikethrough, etc.)

        Returns:
            SafeString with rendered HTML
        """
        if not MISTUNE_AVAILABLE:
            return mark_safe(
                '<div class="cfg-box cfg-box--warning">'
                '<strong>Mistune not installed:</strong> install with: pip install mistune&gt;=3.1.4'
                '</div>'
            )

        if not text:
            return mark_safe('<span class="cfg-muted">No content</span>')

        # Get markdown parser
        md = cls._get_markdown_parser(enable_plugins)
        if not md:
            return mark_safe('<div class="cfg-danger">Error: Could not initialize markdown parser</div>')

        # Render markdown to HTML
        html_content = md(str(text))

        classes = f"cfg-markdown {css_class}".strip()

        # Add container div with max-height if specified
        style = ""
        if max_height:
            style = f'max-height: {max_height}; overflow-y: auto;'

        return format_html(
            '<div class="{}" {}>{}</div>',
            classes,
            mark_safe(f'style="{style}"') if style else '',
            mark_safe(html_content)
        )

    @classmethod
    def render(
        cls,
        content: Union[str, Path],
        collapsible: bool = False,
        title: str = "Documentation",
        icon: str = "description",
        max_height: Optional[str] = "500px",
        enable_plugins: bool = True,
        default_open: bool = False
    ) -> SafeString:
        """
        Universal markdown renderer - auto-detects file vs string content.

        Args:
            content: Markdown string, file path, or Path object
            collapsible: Wrap in collapsible Tailwind details/summary
            title: Title for collapsible section
            icon: Material icon name for title
            max_height: Max height for scrolling (None = no limit)
            enable_plugins: Enable markdown plugins
            default_open: If collapsible, open by default

        Returns:
            Rendered HTML as SafeString

        Examples:
            # Simple render from string
            MarkdownRenderer.render("# Hello\\n\\nThis is **bold**")

            # From file
            MarkdownRenderer.render("/path/to/docs.md")

            # Collapsible documentation
            MarkdownRenderer.render(
                obj.description,
                collapsible=True,
                title="API Documentation",
                icon="api"
            )

            # From file with collapse
            MarkdownRenderer.render(
                "docs/README.md",
                collapsible=True,
                title="Project Documentation",
                default_open=True
            )
        """
        if not content:
            return mark_safe('<span class="cfg-muted">No documentation available</span>')

        # Convert to string if Path object
        content_str = str(content)

        # Try to load from file if it looks like a file path
        markdown_text = content_str
        is_from_file = False

        if cls._is_file_path(content_str):
            file_content = cls._load_from_file(content_str)
            if file_content:
                markdown_text = file_content
                is_from_file = True
            else:
                return format_html(
                    '<div class="cfg-box cfg-box--warning">'
                    '<strong>⚠️ File not found:</strong> {}'
                    '</div>',
                    escape(content_str)
                )

        # Render markdown
        rendered_html = cls.render_markdown(
            markdown_text,
            max_height=max_height if not collapsible else None,
            enable_plugins=enable_plugins
        )

        # Return without collapse if not requested
        if not collapsible:
            return rendered_html

        # Wrap in beautiful collapsible section
        open_attr = 'open' if default_open else ''

        return format_html(
            '<details class="cfg-docs-section" {}>'
            '<summary><span class="cfg-strong">{}</span></summary>'
            '<div{}>{}</div>'
            '</details>',
            mark_safe(open_attr),
            title,
            mark_safe(f' style="max-height: {max_height}; overflow-y: auto;"') if max_height else '',
            rendered_html,
        )

    @classmethod
    def render_docs(
        cls,
        content: Union[str, Path],
        **kwargs
    ) -> SafeString:
        """
        Shorthand for rendering documentation (always collapsible by default).

        Args:
            content: Markdown string or file path
            **kwargs: Additional arguments passed to render()

        Returns:
            Rendered collapsible documentation

        Example:
            def documentation(self, obj):
                return MarkdownRenderer.render_docs(obj.docs_path)
        """
        # Set collapsible=True by default for docs
        if 'collapsible' not in kwargs:
            kwargs['collapsible'] = True

        return cls.render(content, **kwargs)
