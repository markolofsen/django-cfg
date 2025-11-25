"""
JSON display utility.

Renders JSON with syntax highlighting using Pygments.
Supports dual theme (light/dark).
"""

import html as html_lib
import json
from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


def _highlight_json(json_obj: Any, theme: str) -> str:
    """
    Apply syntax highlighting to JSON using Pygments.

    Args:
        json_obj: JSON object to highlight
        theme: Pygments theme name ('colorful' for light, 'monokai' for dark)

    Returns:
        HTML string with highlighted JSON
    """
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer

        formatter = HtmlFormatter(
            style=theme,
            noclasses=True,
            nobackground=True,
            prestyles="white-space: pre-wrap; word-wrap: break-word; font-size: 0.75rem;",
        )
        response = json.dumps(json_obj, indent=2, ensure_ascii=False)
        return highlight(response, JsonLexer(), formatter)

    except ImportError:
        # Fallback to plain JSON if Pygments not available
        formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
        return f'<pre style="font-size: 0.75rem;">{html_lib.escape(formatted_json)}</pre>'


class JSONDisplay:
    """
    Display utility for JSON with syntax highlighting.

    Uses Pygments for highlighting with dual theme support.

    Usage in admin:
        # Via display_fields
        FieldConfig(name="config", ui_widget="json_editor")

        # Or in widgets
        JSONWidgetConfig(field="config", mode="view")
    """

    @classmethod
    def render(
        cls,
        json_value: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render JSON with syntax highlighting.

        Args:
            json_value: JSON value (dict, list, or JSON string)
            config: Configuration options

        Returns:
            HTML string with highlighted JSON
        """
        if not json_value:
            empty_value = config.get('empty_value', "—") if config else "—"
            return empty_value

        config = config or {}

        try:
            # Parse if string
            if isinstance(json_value, str):
                json_obj = json.loads(json_value)
            else:
                json_obj = json_value

            indent = config.get('indent', 2)
            max_display_length = config.get('max_display_length', 100)
            formatted_json = json.dumps(json_obj, indent=indent, ensure_ascii=False)

            # Compact display for short JSON
            if len(formatted_json) <= max_display_length:
                context = {
                    'is_compact': True,
                    'highlighted_light': _highlight_json(json_obj, 'colorful'),
                    'highlighted_dark': _highlight_json(json_obj, 'monokai'),
                }
            else:
                # Preview for long JSON
                escaped_json = html_lib.escape(formatted_json)

                if isinstance(json_obj, dict):
                    context = {
                        'is_compact': False,
                        'preview_type': 'dict',
                        'key_count': len(json_obj),
                        'escaped_json': escaped_json,
                    }
                elif isinstance(json_obj, list):
                    context = {
                        'is_compact': False,
                        'preview_type': 'list',
                        'item_count': len(json_obj),
                        'escaped_json': escaped_json,
                    }
                else:
                    context = {
                        'is_compact': False,
                        'preview_type': 'other',
                        'preview': html_lib.escape(formatted_json[:max_display_length]),
                        'escaped_json': escaped_json,
                    }

            return render_to_string(
                'django_admin/widgets/json_display.html',
                context
            )

        except (json.JSONDecodeError, TypeError, ValueError):
            return mark_safe(f"<code>Invalid JSON: {str(json_value)[:100]}</code>")

    @classmethod
    def from_field(
        cls,
        obj: Any,
        field: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render JSON from model field.

        Args:
            obj: Model instance
            field: Field name
            config: Configuration options

        Returns:
            HTML string with highlighted JSON
        """
        config = config or {}
        json_value = getattr(obj, field, None)
        return cls.render(json_value, config)
