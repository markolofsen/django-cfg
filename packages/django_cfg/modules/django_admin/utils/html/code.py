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
