"""
Code display elements for Django Admin.

Provides inline code and code block rendering with syntax highlighting support.
"""

from typing import Any, Literal, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from . import _classes as C


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
        classes = C.join(C.CODE, css_class)

        return format_html(
            '<code class="{}">{}</code>',
            classes,
            escape(str(text))
        )

    @staticmethod
    def code_block(
        text: Any,
        language: Literal['json', 'python', 'bash', 'javascript', 'html', 'css'] | None = None,
        max_height: Optional[str] = None,
        variant: Literal['default', 'warning', 'danger', 'success', 'info'] = "default",
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
        base_classes = C.box(None if variant == "default" else variant)

        # Add max-height and overflow if specified
        # Add language class for potential syntax highlighting
        lang_class = f"language-{language}" if language else ""
        classes = C.join(base_classes, lang_class)

        if max_height:
            return format_html(
                '<pre class="{}" style="max-height: {}; overflow-y: auto;"><code>{}</code></pre>',
                classes, max_height, str(text),
            )
        return format_html('<pre class="{}"><code>{}</code></pre>', classes, str(text))
