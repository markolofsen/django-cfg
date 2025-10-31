"""
Universal HTML builder for Django Admin display methods.
"""

from pathlib import Path
from typing import Any, List, Optional, Union
import re

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ..icons import Icons
from .markdown_renderer import MarkdownRenderer


class HtmlBuilder:
    """
    Universal HTML builder with Material Icons support and Markdown rendering.

    Usage in admin methods:
        def stats(self, obj):
            return self.html.inline([
                self.html.icon_text(Icons.EDIT, obj.posts_count),
                self.html.icon_text(Icons.CHAT, obj.comments_count),
            ])

        def documentation(self, obj):
            return self.html.markdown_docs(obj.docs_path)
    """

    @staticmethod
    def icon(icon_name: str, size: str = "xs", css_class: str = "") -> SafeString:
        """
        Render Material Icon.

        Args:
            icon_name: Icon name from Icons class
            size: xs, sm, base, lg, xl
            css_class: Additional CSS classes
        """
        size_classes = {
            'xs': 'text-xs',
            'sm': 'text-sm',
            'base': 'text-base',
            'lg': 'text-lg',
            'xl': 'text-xl'
        }
        size_class = size_classes.get(size, 'text-xs')
        classes = f"material-symbols-outlined {size_class}"
        if css_class:
            classes += f" {css_class}"

        return format_html('<span class="{}">{}</span>', classes, icon_name)

    @staticmethod
    def icon_text(icon_or_text: Union[str, Any], text: Any = None,
                  icon_size: str = "xs", separator: str = " ") -> SafeString:
        """
        Render icon with text or emoji with text.

        Args:
            icon_or_text: Icon from Icons class, emoji, or text if text param is None
            text: Optional text to display after icon
            icon_size: Icon size (xs, sm, base, lg, xl)
            separator: Separator between icon and text

        Usage:
            html.icon_text(Icons.EDIT, 5)  # Icon with number
            html.icon_text("📝", 5)  # Emoji with number
            html.icon_text("Active")  # Just text
        """
        if text is None:
            # Just text
            return format_html('<span>{}</span>', escape(str(icon_or_text)))

        # Check if it's a Material Icon (from Icons class) or emoji
        icon_str = str(icon_or_text)

        # Detect if it's emoji by checking for non-ASCII characters
        is_emoji = any(ord(c) > 127 for c in icon_str)

        if is_emoji or icon_str in ['📝', '💬', '🛒', '👤', '📧', '🔔', '⚙️', '🔧', '📊', '🎯']:
            # Emoji
            icon_html = escape(icon_str)
        else:
            # Material Icon
            icon_html = HtmlBuilder.icon(icon_str, size=icon_size)

        return format_html('{}{}<span>{}</span>', icon_html, separator, escape(str(text)))

    @staticmethod
    def inline(items: List[Any], separator: str = " | ",
               size: str = "small", css_class: str = "") -> SafeString:
        """
        Render items inline with separator.

        Args:
            items: List of SafeString/str items to join
            separator: Separator between items
            size: small, medium, large
            css_class: Additional CSS classes

        Usage:
            html.inline([
                html.icon_text(Icons.EDIT, 5),
                html.icon_text(Icons.CHAT, 10),
            ])
        """
        if not items:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        size_classes = {
            'small': 'text-xs',
            'medium': 'text-sm',
            'large': 'text-base'
        }
        size_class = size_classes.get(size, 'text-xs')

        classes = size_class
        if css_class:
            classes += f" {css_class}"

        # Convert items to strings, keeping SafeString as-is
        from django.utils.safestring import SafeString, mark_safe
        processed_items = []
        for item in items:
            if isinstance(item, (SafeString, str)):
                processed_items.append(item)
            else:
                processed_items.append(escape(str(item)))

        # Join with separator
        joined = mark_safe(separator.join(str(item) for item in processed_items))

        return format_html('<span class="{}">{}</span>', classes, joined)

    @staticmethod
    def span(text: Any, css_class: str = "") -> SafeString:
        """
        Render text in span with optional CSS class.

        Args:
            text: Text to display
            css_class: CSS classes
        """
        if css_class:
            return format_html('<span class="{}">{}</span>', css_class, escape(str(text)))
        return format_html('<span>{}</span>', escape(str(text)))

    @staticmethod
    def div(content: Any, css_class: str = "") -> SafeString:
        """
        Render content in div with optional CSS class.

        Args:
            content: Content to display (can be SafeString)
            css_class: CSS classes
        """
        if css_class:
            return format_html('<div class="{}">{}</div>', css_class, content)
        return format_html('<div>{}</div>', content)

    @staticmethod
    def link(url: str, text: str, css_class: str = "", target: str = "") -> SafeString:
        """
        Render link.

        Args:
            url: URL
            text: Link text
            css_class: CSS classes
            target: Target attribute (_blank, _self, etc)
        """
        if target:
            return format_html(
                '<a href="{}" class="{}" target="{}">{}</a>',
                url, css_class, target, escape(text)
            )
        return format_html('<a href="{}" class="{}">{}</a>', url, css_class, escape(text))

    @staticmethod
    def badge(text: Any, variant: str = "primary", icon: Optional[str] = None) -> SafeString:
        """
        Render badge with optional icon.

        Args:
            text: Badge text
            variant: primary, success, warning, danger, info, secondary
            icon: Optional Material Icon

        Usage:
            html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        """
        variant_classes = {
            'success': 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200',
            'warning': 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200',
            'danger': 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200',
            'info': 'bg-info-100 text-info-800 dark:bg-info-900 dark:text-info-200',
            'primary': 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200',
            'secondary': 'bg-base-100 text-font-default-light dark:bg-base-800 dark:text-font-default-dark',
        }

        css_classes = variant_classes.get(variant, variant_classes['primary'])

        icon_html = ""
        if icon:
            icon_html = format_html('<span class="material-symbols-outlined text-xs mr-1">{}</span>', icon)

        return format_html(
            '<span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {}">{}{}</span>',
            css_classes, icon_html, escape(str(text))
        )

    @staticmethod
    def empty(text: str = "—") -> SafeString:
        """Render empty/placeholder value."""
        return format_html(
            '<span class="text-font-subtle-light dark:text-font-subtle-dark">{}</span>',
            escape(text)
        )

    @staticmethod
    def code(text: Any, css_class: str = "") -> SafeString:
        """
        Render inline code.

        Args:
            text: Code text
            css_class: Additional CSS classes

        Usage:
            html.code("/path/to/file")
            html.code("command --arg value")
        """
        base_classes = "font-mono text-xs bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded"
        classes = f"{base_classes} {css_class}".strip()

        return format_html(
            '<code class="{}">{}</code>',
            classes,
            escape(str(text))
        )

    @staticmethod
    def code_block(
        text: Any,
        language: Optional[str] = None,
        max_height: Optional[str] = None,
        variant: str = "default"
    ) -> SafeString:
        """
        Render code block with optional syntax highlighting and scrolling.

        Args:
            text: Code content
            language: Programming language (json, python, bash, etc.) - for future syntax highlighting
            max_height: Max height with scrolling (e.g., "400px", "20rem")
            variant: Color variant - default, warning, danger, success, info

        Usage:
            html.code_block(json.dumps(data, indent=2), language="json")
            html.code_block(stdout, max_height="400px")
            html.code_block(stderr, max_height="400px", variant="warning")
        """
        # Variant-specific styles
        variant_classes = {
            'default': 'bg-base-50 dark:bg-base-900 border-base-200 dark:border-base-700',
            'warning': 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-700',
            'danger': 'bg-danger-50 dark:bg-danger-900/20 border-danger-200 dark:border-danger-700',
            'success': 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-700',
            'info': 'bg-info-50 dark:bg-info-900/20 border-info-200 dark:border-info-700',
        }

        variant_class = variant_classes.get(variant, variant_classes['default'])

        # Base styles
        base_classes = f"font-mono text-xs whitespace-pre-wrap break-words border rounded-md p-3 {variant_class}"

        # Add max-height and overflow if specified
        style = ""
        if max_height:
            style = f'style="max-height: {max_height}; overflow-y: auto;"'

        # Add language class for potential syntax highlighting
        lang_class = f"language-{language}" if language else ""

        return format_html(
            '<pre class="{} {}" {}><code>{}</code></pre>',
            base_classes,
            lang_class,
            style,
            escape(str(text))
        )

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
        return MarkdownRenderer.render_markdown(
            text=text,
            css_class=css_class,
            max_height=max_height,
            enable_plugins=enable_plugins
        )

    @staticmethod
    def uuid_short(uuid_value: Any, length: int = 6, show_tooltip: bool = True) -> SafeString:
        """
        Shorten UUID to first N characters with optional tooltip.

        Args:
            uuid_value: UUID string or UUID object
            length: Number of characters to show (default: 6)
            show_tooltip: Show full UUID on hover (default: True)

        Usage:
            html.uuid_short(obj.id)  # "a1b2c3..."
            html.uuid_short(obj.id, length=8)  # "a1b2c3d4..."
            html.uuid_short(obj.id, show_tooltip=False)  # Just short version

        Returns:
            SafeString with shortened UUID
        """
        uuid_str = str(uuid_value)

        # Remove dashes for cleaner display
        uuid_clean = uuid_str.replace('-', '')

        # Take first N characters
        short_uuid = uuid_clean[:length]

        if show_tooltip:
            return format_html(
                '<code class="font-mono text-xs bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded cursor-help" title="{}">{}</code>',
                uuid_str,
                short_uuid
            )

        return format_html(
            '<code class="font-mono text-xs bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded">{}</code>',
            short_uuid
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
        return MarkdownRenderer.render(
            content=content,
            collapsible=collapsible,
            title=title,
            icon=icon,
            max_height=max_height,
            enable_plugins=enable_plugins,
            default_open=default_open
        )
