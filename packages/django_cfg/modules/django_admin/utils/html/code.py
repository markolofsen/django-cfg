"""
Code display elements for Django Admin.

Provides inline code and code block rendering with syntax highlighting support.
"""

from typing import Any, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class CodeElements:
    """Code display elements."""

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
        # Unfold-compatible Tailwind CSS classes
        variant_classes = {
            'default': 'bg-base-50 dark:bg-base-900 border-base-200 dark:border-base-700',
            'warning': 'bg-orange-50 dark:bg-orange-500/20 border-orange-200 dark:border-orange-500/30',
            'danger': 'bg-red-50 dark:bg-red-500/20 border-red-200 dark:border-red-500/30',
            'success': 'bg-green-50 dark:bg-green-500/20 border-green-200 dark:border-green-500/30',
            'info': 'bg-blue-50 dark:bg-blue-500/20 border-blue-200 dark:border-blue-500/30',
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
